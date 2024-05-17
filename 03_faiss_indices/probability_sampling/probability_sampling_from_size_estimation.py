#!/usr/bin/python3
"""
Author: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""
import sys, os
import utils
import numpy as np 
import math
import glob
from npy_append_array import NpyAppendArray

# all functions that were not modified, are imported from previous version
from probability_sampling import read_manifest, remove_existing_files, generate_probability_distribution 
from probability_sampling import load_datasets, write_language_manifest

# FOLDERS HARDCODED FOR SIMPLICITY; THIS IS USED TO FETCH STATISTICS NECESSARY FOR THE COMPUTATION
from probability_sampling import stats_json

#CHANGE RANDOM SEED HERE
np.random.seed(1)

############ ESTIMATING MFCC
label_rate_mfcc = 100
feature_size_39 = 156

########### ESTIMATING TRANSFORMER VECTOR
label_rate_transformer = 50
feature_size_768 = 3072 

###########
sample_rate = 16000

def compute_estimated_size(dataset_manifest, mfcc=False):
    if mfcc:
        label_rate = label_rate_mfcc
        feature_size = feature_size_39
    else:
        label_rate = label_rate_transformer
        feature_size = feature_size_768
    
    sizes = list()
    for _, _, size in dataset_manifest:
        number_of_instances = int((float(size)/ sample_rate) * label_rate)
        size_entry = number_of_instances * feature_size
        sizes.append(size_entry)
    return sizes

def produce_indices_with_mem_limit(estimated_size, mem_limit):

    dataset_size = sys.getsizeof(estimated_size) #adds the length of a list structure with numpy_features length, the content is not relevant at this point
    dataset_size += sum([element for element in estimated_size])
    dataset_size /= (1024**3) #bytes to gbytes

    print("\t", "The full dataset (loaded in nested list) in GB is", dataset_size)

    length = len(estimated_size)

    percentage = mem_limit / dataset_size

    print("\t", "hence, we will repeat the dataset:", percentage)
    allocated_mem = 0.0

    #more than one copy of the dataset goes inside
    if percentage > 0:
        #produces the copies already shuffled
        sampled_indices = list(np.random.permutation( np.repeat(np.arange(length), int(percentage)) ) )
        allocated_mem += int(percentage) * dataset_size

    #this gets over the extra indices we have to sample
    
    if percentage % 1 > 0:
        while allocated_mem < mem_limit:
            #sample index
            index = np.random.choice(length, 1, replace=False)[0]
            
            #get size
            size_utt = estimated_size[index] / (1024**3)
            if allocated_mem + size_utt < mem_limit:
                allocated_mem += size_utt
                sampled_indices.append(index)
            else:
                break
    print("\t", "Total allocated memory", allocated_mem)
    print("\t", "Number of samples entries", len(sampled_indices))

    return sampled_indices, allocated_mem

def sample_with_mem_target(dataset_manifest, estimated_size, dataset_mem_proportion):
    #produces indices for sampling

    #numpy_features is a list of variable sizes (in bytes) loaded by load_feature_shard_size 
    indices, estimated_total = produce_indices_with_mem_limit(estimated_size, dataset_mem_proportion)

    new_manifest = [dataset_manifest[index] for index in indices]

    #then return size
    return new_manifest, estimated_total

def sample_language_datasets(manifest_root, language_distribution, language, dataset, upsampling_dataset, output_root, mem_target, mfcc):
    #computes the amount of memory in GB from the max TARGET that language can use
    language_mem_proportion = mem_target*language_distribution[language]
    
    #load the datasets
    datasets = load_datasets(dataset, language)

    #define numpy folder where we will dump everything
    feat_path = output_root + "/features/" + language

    #we save in append mode, so we need to make sure we are not duplicating data
    remove_existing_files(feat_path)

    #computes dataset distribution
    datasets_distribution = generate_probability_distribution(datasets, upsampling_dataset)
    
    print("Starting language", language, "with following upsampling probability", language_distribution[language])
    print("\t", "There is/are", len(datasets_distribution), "datasets with probabilities", list(datasets_distribution.values()))
    
    manifests = dict()

    required_mem = 0.0
    #for each dataset
    for sub_dataset in datasets:
        #gets dataset root
        dataset_root = "/".join(sub_dataset.split("/")[:-1]) #last one is the json

        #load manifest
        dataset_manifest = read_manifest(manifest_root + dataset_root + ".tsv")
        estimated_size = compute_estimated_size(dataset_manifest, mfcc=mfcc)

        assert len(estimated_size) == len(dataset_manifest)

        #get memory chunk dedicated for this dataset
        dataset_mem_proportion = language_mem_proportion*datasets_distribution[sub_dataset]
        print("\t", "The", sub_dataset, "mem proportion:", dataset_mem_proportion)

        #sample and write new numpy files
        new_manifest, dump_size = sample_with_mem_target(dataset_manifest, estimated_size, dataset_mem_proportion)

        assert dump_size < dataset_mem_proportion

        manifests[sub_dataset] = new_manifest

        required_mem += dump_size

        print("\n")
    assert required_mem < language_mem_proportion

    print("\t", "Writing", output_root + "/manifest/" + language +".tsv")
    write_language_manifest(output_root + "/manifest/"+ language +".tsv", manifests, language)

if __name__ == '__main__':
    print(sys.argv)
    manifest_root=sys.argv[1]
    output_root=sys.argv[2]
    language=sys.argv[3]
    upsampling_language = float(sys.argv[4])
    upsampling_dataset = float(sys.argv[5]) 
    mem_target=float(sys.argv[6]) #gb
    if sys.argv[7] == "True":
        mfcc_flag = True
    elif sys.argv[7] == "False":
        mfcc_flag = False
    else:
        print("ERROR ON MFCC FLAG ARG")
        print(sys.argv)
        exit(1)
    seed = int(sys.argv[8]) 
    np.random.seed(seed)

    #True for first iteration, false otherwise
    dataset = utils.load_json(stats_json)
    
    #computes the language distribution with upsampling factor
    language_distribution = generate_probability_distribution(dataset, upsampling_language)

    if len(language) == 1: 
        #character case
        languages_subset = [key for key in dataset if key[0] == language]
        for language in languages_subset:
            sample_language_datasets(manifest_root, language_distribution, language, dataset, upsampling_dataset, output_root, mem_target, mfcc_flag)

    else:
        sample_language_datasets(manifest_root, language_distribution, language, dataset, upsampling_dataset, output_root, mem_target, mfcc_flag)

        