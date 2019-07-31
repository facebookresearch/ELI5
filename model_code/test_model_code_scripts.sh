# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
# Note: this script assumes you have already created the dataset following the data creation scripts. 

python process_data_to_source_target.py --input testing_files --output testing_files

python compute_rouge.py --hypotheses testing_files/test_rouge_input.txt --references testing_files/test_rouge_answer.txt

python pos_tag.py --input testing_files --output testing_files --dataset-name test

python prepare_multitask_input.py --input testing_files/raw_input_for_multitask.txt --output testing_files/output_for_multitask.txt
subword-nmt apply-bpe -c bpe_codes.txt < testing_files/output_for_multitask.txt > testing_files/output_for_multitask_bpe.txt
cat testing_files/output_for_multitask_bpe.txt | python ~/fairseq/interactive.py ~/fairseq/data-bin/eli5_data --path multitask_checkpoint.pt  --task translation --batch-size 16 --nbest 1 --beam 5 --source-lang multitask_source_bpe --target-lang multitask_target_bpe --nbest 1 --prefix-size 0 --remove-bpe --max-len-b 500 --max-len-a 0 --min-len 250 --buffer-size 1 --batch-size 1 --no-repeat-ngram-size 3
