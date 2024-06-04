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

Pre-trained models with trained faiss indices: https://huggingface.co/collections/utter-project/mhubert-147-models-665f1c1dea9a5601a1bfc905

Manifest files: https://huggingface.co/utter-project/mHuBERT-147-base-3rd-iter/tree/main/manifest

## Citation

```
@inproceedings{boito2024mhubert,
author={Marcely Zanon Boito, Vivek Iyer, Nikolaos Lagos, Laurent Besacier, Ioan Calapodescu},
title={{mHuBERT-147: A Compact Multilingual HuBERT Model}},
year=2024,
booktitle={Interspeech 2024},
}
```

## Funding
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/1200px-Flag_of_Europe.svg.png" width=10% height=10%> 

This is an output of the European Project UTTER (Unified Transcription and Translation for Extended Reality) funded by European Union’s Horizon Europe Research and Innovation programme under grant agreement number 101070631.

For more information please visit https://he-utter.eu/


