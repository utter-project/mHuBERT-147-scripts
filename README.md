# mHuBERT-147 scripts

Collection of pre-processing scripts for mHuBERT-147 training.

1. Prepare your dataset: filter out long and short utterances; convert audio files to the right format and sampling rate.
See **01_dataset_preproc** for the scripts used for the different datasets inside mHuBERT-147.

2. Extract features using either MFCC (1st iteration) or a (m)HuBERT checkpoint.
See launchers at **02_feature_extraction**.

3. Train a faiss index. See examples of probability sampling, training and assignment at **03_faiss_indices**.

4. Package your data for training. See example in **04_packaging** for creating the validation set for training (5 files per dataset/language).

5. Train using our fairseq fork using the information at **05_training**.
Fairseq fork for training: https://github.com/utter-project/fairseq

6. Evaluate it!

## Other Resources

Pre-trained models with trained faiss indices: TO DO LINK OF COLLECTION

Manifest files: TO DO LINK HERE

## Citation

```
TO DO
```
