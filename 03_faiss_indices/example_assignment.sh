#!/bin/bash
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --cpus-per-task=4
#SBATCH --mem=500G
#SBATCH --output=index_application_mmhubert_%j.log
#SBATCH --time=360:00:00


conda activate faiss_env

FEATURES=$1 #.npy file
INDEX=$2
OUTPUT=$3


python apply_index_per_file.py $FEATURES $INDEX $OUTPUT
