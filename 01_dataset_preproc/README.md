# Dataset preprocessing

This folder contains a collection of scripts that help on speech data pre-processing. For each dataset, we convert the audio files into wav files, and produce json files listing the entries and their metadata.

* audio_scripts
Scripts for converting the different audio formats into wav.

* dataset_specific_preproc
Scripts for producing (dataset,language) json files listing wav files and metadata.

* unified_preproc
Scripts for filtering and concatenating utterances inside dataset jsons.


## General pipeline

1. Transform your audio files using script at audio_scripts
2. For each language in your dataset, use dataset_specific_preproc to produce train.json listing trainable utterances
3. Use unified_preproc/filter_json_files.py to filter this json for valid utterances [2,30]. If many short utterances are presented, these can be concatenated using unified_preproc/concat_wav_files.py
4. Once this step is done for all languages inside a dataset, the dataset json can be generated using unified_preproc/generate_dataset_stats.py
5. Once the same is done for all datasets you are working with, unified_preproc/generate_mhubert_stats.py can be run, producing the final statistics over the dataset (used for sampling in 03_faiss_indices)