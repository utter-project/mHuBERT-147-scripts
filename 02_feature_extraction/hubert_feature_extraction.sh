#!/bin/bash

# TO FILL
MANIFEST_ROOT= # FORMAT MANIFEST_ROOT/DATASET_X/MANIFEST.TSV
OUTPUT_ROOT="features/" # OUTPUT FOLDER
CHECKPOINT="checkpoint_last.pt" # YOUR CHECKPOINT GOES HERE
# TO FILL


LAYER=6 #6 for 2nd iteration; 9 for 3rd iteration

cd $MANIFEST_ROOT
for folder in *;
do
    sbatch extract_hubert_by_dataset.sh $folder $OUTPUT_ROOT $CHECKPOINT $LAYER
done



