#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito, Nikolaos Lagos

Copyright NAVER LABS Europe 2023

"""

import sys
import numpy as np 
import glob
import gc

from faiss_index_creation import *


def load_all_features(features_dir):
    #this requires over 4TB of RAM
    datasets = glob.glob(features_dir + "/*")
    features = dict()
    for dataset in datasets:
        language_paths = glob.glob(dataset + "/*-feats/*.npy")
        for language_path in language_paths:
            features[language_path] = dict()
            features[language_path]["features"] = load_feature(language_path)
            features[language_path]["lengths"] = load_lengths(language_path.replace(".npy",".len"))
    return features


if __name__ == '__main__':
    ####################### params
    features_dir = sys.argv[1]
    index_dir =  sys.argv[2]
    index_path = index_dir + "/mmhubert.index"
    K=sys.argv[3]
    compression = int(sys.argv[4])
    ####################### params
    

    feature_files = glob.glob(features_dir + "/*.npy")


    print("LOADING FEATURE FILES:", len(feature_files))
    #this version of the code is probably duplicating memory footprint, trying the solution below instead
    
    #replaced concatenate by vstack
    f = load_feature(feature_files[0])
    print("current number of features:", len(f))
    for i in range(1,len(feature_files)):
        #f = np.concatenate((f, load_feature(feature_files[i])), axis=0)
        f = np.vstack((f, load_feature(feature_files[i])))
        print("current number of features:", len(f))
        gc.collect()
    
    
    if compression == 1:
        STRONG_COMPRESSION_MODE = "OPQ16_64,IVF"+K+"_HNSW32,PQ16x4fsr" 
        compression = STRONG_COMPRESSION_MODE
    elif compression == 0:
        WEAK_COMPRESSION_MODE = "OPQ32_64,IVF"+K+"_HNSW32,PQ32x8"
        compression = WEAK_COMPRESSION_MODE
    else:
        print("ERROR: INVALID COMPRESSION TYPE")
        exit(1)
    # 2. INDEX AND PRODUCE CENTROIDS

    # Get centroids of our data either using an index or k-means independently 
    print("CREATING INDEX")
    index, index_ivf = create_index(f, compression) 

    print("WRITING INDEX")
    write_index(index, index_path)







