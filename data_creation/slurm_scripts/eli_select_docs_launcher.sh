# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

for nm in 'explainlikeimfive' 'AskHistorians' 'askscience'
do
    for c in {0..99}
    do
        sbatch --export=ALL,NM=$nm,C=$c eli_select_docs.sbatch
    done
done
