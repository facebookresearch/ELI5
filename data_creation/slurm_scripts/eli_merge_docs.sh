# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

cd /checkpoint/yjernite/Code/ELI5/data_creation
pwd
echo $NM
echo $C
python merge_support_docs.py $NM $C
