#!/bin/bash
#SBATCH -p gpu
#SBATCH --gres=gpu:8
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --output=feature_extraction_%j.log


conda activate <environment>

folder=$1
root_output_folder=$2
checkpoint=$3
layer=$4


fairseq_dir=<path> #https://github.com/utter-project/fairseq


folder_basename=$(basename $folder)
output_folder=$root_output_folder/$folder_basename

cd $folder
for lang in *.tsv; 
do
    lang_basename=$(basename $lang)
    prefix="${lang_basename%.*}"
    #no sharding in this example
    echo python $fairseq_dir/examples/hubert/simple_kmeans/dump_hubert_feature.py $lang $prefix $checkpoint $layer 1 0 $output_folder/$prefix-feats
done
