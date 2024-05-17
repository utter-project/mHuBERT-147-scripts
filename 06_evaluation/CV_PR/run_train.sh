#!/bin/bash
#SBATCH -p gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --constraint="gpu_v100&gpu_32g"
#SBATCH --output=log_train_%j_asr_cv.log


conda activate <environment>


python my_train.py hparams/<config>.yaml
