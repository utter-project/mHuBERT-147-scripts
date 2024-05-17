#!/bin/bash
#SBATCH -p cpu
#SBATCH --mem=32G
#SBATCH --output=sampling_%j.log
#SBATCH --time=360:00:00


MANIFEST_FOLDER=$1
OUTPUT_FOLDER=$2
PREFIX=$3
LANGUAGE_UPSAMPLING=$4
DATASET_UPSAMPLING=$5
BUDGET=$6


conda activate <environment>


python probability_sampling_from_size_estimation.py $MANIFEST_FOLDER $OUTPUT_FOLDER $PREFIX $LANGUAGE_UPSAMPLING $DATASET_UPSAMPLING $BUDGET
