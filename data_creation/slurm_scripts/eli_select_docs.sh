# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

cd /checkpoint/yjernite/Code/ELI5/data_creation
pwd
echo $NM
echo $C
echo $NS
echo $NC
python select_sentences_tfidf.py -sr_n $NM -sid $C -ns $NS -nc $NC
