#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito, Nikolaos Lagos

Copyright NAVER LABS Europe 2023

"""

import sys
from faiss_index_creation import *



if __name__ == '__main__':
    ####################### params
    features_file = sys.argv[1]
    index_path = sys.argv[2]
    output_folder = sys.argv[3]
    ####################### params

    f =  load_feature(features_file)
    l = load_lengths(features_file.replace(".npy",".len"))
    
    index, index_ivf = load_index(index_path)

    _,C = get_centroids_index(f, index, index_ivf) # Index based

    vecs = apply_centroids_to_audios(l, C)
    
    element = features_file.split("/")[-1].split(".npy")[0]
    write_label_file(vecs, output_folder + "/" + element + ".km")