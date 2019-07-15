#!/bin/bash
#SBATCH --job-name=extract
#SBATCH --nodes=1 --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=logs/download_docs.out
#SBATCH --error=logs/download_docs.err

./eli_download_docs.sh
