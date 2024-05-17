# Working with Faiss

This folder contain the scripts necessary for running faiss clustering and label application.

1. Requirements: Install 00_requirements/faiss_requirements.txt

2. (before clustering, optional) Up-sampling your data for clustering: See 03_faiss_indices/probability_sampling/probability_sampling_from_size_estimation.py 

You will need your dataset statistics compiled in a json, such as in 03_faiss_indices/probability_sampling/hubert_stats_oct2023.json. See how to produce this json in 01_dataset_preproc/README.md

3. Clustering: see 03_faiss_indices/example_training.sh

4. Assignment: see 03_faiss_indices/example_assignment.sh
