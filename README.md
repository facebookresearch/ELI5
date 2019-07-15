<img src="eli5.png" width="150">

# Data creation

We provide a suite of scripts to download paired questions and answers from the ELI5 subreddit along with supporting documents from the CommonCrawl

## Downloading the Reddit Data

The first step consists in downloading the Reddit Data drom the files provided at pushshift.io for all months from 07/2011 to 07/2018. This is done by running:

```
python download_reddit_qalist.py -Q
python download_reddit_qalist.py -A
```
The first line takes about 6 hours on one machine to download the quations, and the second less than 48 hours for the answers. Pushshift files are automatically removed after they've been processed, so space shouldn't be an issue there. The final product should be 689MB.


## Downloading support documents

We provide a list of CommonCrawl IDs for supporting documents for each of the questions (TODO: actually upload). This can be obtained at:
```
cd precomputed
curl https://dl.fbaipublicfiles.com/eli5qa/eli5_url_cidmap.tar.gz | tar xvzf -
cd ..
```

The next step than consists in reading through the CommonCrawl WET files to gather the text of pages which are used as support documents. In order to gather the 100 documents for each QA pair using a SLURM cluster and 72 threads, run:
```
cd slurm_scripts
./eli_download_docs_master.sh
```

We also provide an equivalent script to only download the documents we actually used after running our heuristic passage selection (cf. paper)
```
cd slurm_scripts
./eli_download_docs_small_master.sh
```

## Finalizing the dataset

All that remains to do now is to map the collected passages to the question-answer pairs and, apply our provided heuristic to make a single support document to select relevant passages
```
python make_qda_shelve.py -so
```
Unfortunately, this relies on building a shelve file gathering all of the relevant web articles for each QA-pair, which does not support concurrent write and cannot be parallelized easily, so the whole process should take about 24 hours. The results will be located in the processed\_data folder.

Congrats, you can now start working on your very own Long-Form Question Answering systems!

# Modeling with Fairseq-py

## Formatting data files

We provide a script to convert the json formatted files to .txt files for source and target and build the multi-tasking source-target pairs. Modify the input and output path accordingly.
```
cd release_data_scripts/model_code
OUTPUT_PATH=formatted_files
PATH_TO_DATA=processed_data
mkdir OUTPUT_PATH
python process_data_to_source_target.py --input $PATH_TO_DATA --output $OUTPUT_PATH
```

## Applying BPE

We use [bpe](https://github.com/rsennrich/subword-nmt) and release the BPE codes we used. You will need to apply BPE on the data. We provide a sample command:

```
subword-nmt apply-bpe -c model_code/bpe_codes.txt < formatted_files/train.qd_source > formatted_files/train.qd_source_bpe
subword-nmt apply-bpe -c model_code/bpe_codes.txt < formatted_files/test.qd_source > formatted_files/test.qd_source_bpe
subword-nmt apply-bpe -c model_code/bpe_codes.txt < formatted_files/valid.qd_source > formatted_files/valid.qd_source_bpe
subword-nmt apply-bpe -c model_code/bpe_codes.txt < formatted_files/train.qd_target > formatted_files/train.qd_target_bpe
subword-nmt apply-bpe -c model_code/bpe_codes.txt < formatted_files/test.qd_target > formatted_files/test.qd_target_bpe
subword-nmt apply-bpe -c model_code/bpe_codes.txt < formatted_files/valid.qd_target > formatted_files/valid.qd_target_bpe
```

## Training and Generating with Fairseq-py

We use the [Fairseq-py](https://github.com/pytorch/fairseq) sequence-to-sequence library. For details about this library, please see the main repository or read the [full documentation](https://fairseq.readthedocs.io/en/latest/). We provide example commands below. Please modify the paths accordingly to where you have stored the data, where you would like the binarized data to be located, and where the trained model checkpoints have been stored.

To binarize the data:
```
cd fairseq
TEXT=formatted_files
python preprocess.py --source-lang qd_source_bpe --target-lang qd_target_bpe \
   --validpref $TEXT/valid --testpref $TEXT/test --trainpref $TEXT/train --destdir data-bin/eli5
```

To train the model:
```
cd fairseq
python train.py data-bin/eli5 --task translation --source-lang qd_source_bpe --target-lang qd_target_bpe --arch transformer_wmt_en_de_big_t2t --share-decoder-input-output-embed --dropout 1e-1 --attention-dropout 1e-1 --relu-dropout 1e-1 --criterion label_smoothed_cross_entropy --label-smoothing 1e-1 --optimizer adam --adam-betas '(0.9, 0.98)' --lr 1e-4 --lr-scheduler inverse_sqrt --warmup-updates 4000 --warmup-init-lr 1e-7 --min-lr 1e-9 --clip-norm 0 --no-progress-bar --log-interval 100
```

To generate from the model:
```
cd fairseq
PATH_TO_CHECKPOINT=model_checkpoint.pt
python generate.py data-bin/eli5 --path $PATH_TO_CHECKPOINT --gen-subset valid --task translation --nbest 1 --source-lang qd_source_bpe --target-lang qd_target_bpe --beam 5 --batch-size 32 --remove-bpe --no-repeat-ngram-size 3 --max-len-b 500 --min-len 200
```
to evaluate on the test set, set:
```
--gen-subset test
```

## Evaluating ROUGE
We provide a script used to compute ROUGE. Given a file of model generated hypotheses and a file of true references, it can be run in the following manner:
```
pip install rouge
HYPOTHESES=model_hypotheses.txt
REFERENCES=true_references.txt
python compute_rouge.py --hypotheses $HYPOTHESES --references $REFERENCES
```

## How to use the Multi-task Pretrained Model
We provide a pretrained model, which you can download here:
```
wget https://dl.fbaipublicfiles.com/eli5qa/multitask_checkpoint.pt
```

To use the pretrained model, you will need to follow these steps:

First, the multi-task model requires labeling the source with the task label (e.g. question answering v. language modeling). We provide a script here to do this:
```
python model_code/prepare_multitask_input.py --input $DATA_FILE --output $OUTPUT_DATA_FILE
```

Then, apply the BPE:
```
subword-nmt apply-bpe -c model_code/bpe_codes.txt < $OUTPUT_DATA_FILE > $OUTPUT_DATA_FILE_BPE
```

Now, you are ready to forward the model on your BPE'd data.
