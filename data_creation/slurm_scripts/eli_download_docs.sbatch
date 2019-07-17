#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
#SBATCH --job-name=extract
#SBATCH --nodes=1 --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=48:00:00
#SBATCH --output=logs/download_docs_%A.out
#SBATCH --error=logs/download_docs_%A.err

./eli_download_docs.sh
