#!/bin/bash
#SBATCH -p cpu
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --output=feature_extraction_%j.log


conda activate <environment>


ROOT=$1

fairseq_dir=<path> #https://github.com/utter-project/fairseq

cd $ROOT

for language in *.tsv; 
do
    python $fairseq_dir/examples/hubert/simple_kmeans/dump_mfcc_feature.py \
    ./ \
    ${language%.*} 1 0 ${language%.*}-feats/

done


