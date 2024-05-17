#!/bin/bash
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --cpus-per-task=8
#SBATCH --mem=1700G
#SBATCH --output=index_creation%j.log


conda activate faiss_env

ROOT=<ADD HERE>

FEATURES="$ROOT/features/"
OUTPUT="$ROOT/faiss_index_850gb/"

COMPRESSION=1 # 1-> STRONG; 0 -> WEAK
K=1000 

mkdir $OUTPUT

python create_mmhubert_index.py $FEATURES $OUTPUT $K $COMPRESSION