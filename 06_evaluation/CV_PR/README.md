# Few-shot phoneme recognition

1. Prepare the data.
Download the labels: https://dl.fbaipublicfiles.com/cpc_audio/common_voices_splits.tar.gz
Download the commonvoice splits: https://commonvoice.mozilla.org/en/datasets

Labels original source: https://github.com/facebookresearch/CPC_audio?tab=readme-ov-file
Citation:
```
@INPROCEEDINGS{9054548,
  author={Rivière, Morgane and Joulin, Armand and Mazaré, Pierre-Emmanuel and Dupoux, Emmanuel},
  booktitle={ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)}, 
  title={Unsupervised Pretraining Transfers Well Across Languages}, 
  year={2020},
  volume={},
  number={},
  pages={7414-7418},
  keywords={Training;Signal processing algorithms;Signal processing;Predictive coding;Feature extraction;Task analysis;Speech processing;Unsupervised pretraining;low resources;cross-lingual},
  doi={10.1109/ICASSP40776.2020.9054548}}
```

2. Install requirements for speechbrain training. See 00_requirements/speechbrain_requirements.txt
Please take notice that this recipe uses speechbrain<1.0.

3. Train language-specific few-shot phoneme recognition systems using the 1h train, valid and test sets.