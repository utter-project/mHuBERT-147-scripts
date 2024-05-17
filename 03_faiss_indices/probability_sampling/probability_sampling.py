#!/usr/bin/python3
"""
Author: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys, os
import utils
import numpy as np 
import math
from npy_append_array import NpyAppendArray


# FOLDERS HARDCODED FOR SIMPLICITY; THIS IS USED TO FETCH STATISTICS NECESSARY FOR THE COMPUTATION
#root folder for the collection of dataset json files (see 01_dataset_preproc)
ROOT="PATH/" 

#stats json such as the one in the example, it contains the list of jsons that are at ROOT
stats_json="hubert_stats_oct2023.json" 


def read_manifest(f_path):
    #note the manifest has the frames after the tab, not separated here for convenience
    lines = [line.strip() for line in open(f_path)]
    header = [lines[0]]
    content = lines[1:]
    return [header + line.split("\t") for line in content]

def load_feature_shard(feat_dir, split, nshard, rank):
    feat_path = f"{feat_dir}/{split}_{rank}_{nshard}.npy"
    leng_path = f"{feat_dir}/{split}_{rank}_{nshard}.len"
    with open(leng_path, "r") as f:
        lengs = [int(line.rstrip()) for line in f]
        offsets = [0] + np.cumsum(lengs[:-1]).tolist()

    indices = np.array([i for i in range(0,len(lengs))]) 
    feat = np.load(feat_path) 
    features = [feat[offsets[i]: offsets[i] + lengs[i]] for i in indices]

    return features

def load_feature(feat_dir):
    split = feat_dir.split("/")[-1].replace("-feats","")
    return load_feature_shard(feat_dir, split, 1, 0)

def generate_probability_distribution(dataset, upsampling):
    prob_sum = 0
    language_distribution = dict()
    total_duration = sum([dataset[key]["duration"] for key in dataset])

    for language in dataset:
        proportion = (dataset[language]["duration"]/total_duration)**upsampling
        language_distribution[language] = proportion
        prob_sum += proportion
        
    for language in language_distribution:
        language_distribution[language] /= prob_sum
    
    return language_distribution

def load_datasets(dataset, language):
    jsons = dict()
    for entry in dataset[language]["json"]:
        path = ROOT + entry
        jsons[entry] = dict()
        jsons[entry]["content"] = utils.load_json(path)
        jsons[entry]["duration"] = sum([jsons[entry]["content"][key]["duration"] for key in jsons[entry]["content"]])/3600 #transform in hours
    return jsons

def produce_indices_with_mem_limit(mfcc_features, mem_limit):

    dataset_size = sys.getsizeof(mfcc_features)
    for nested in mfcc_features:
        dataset_size += nested.nbytes #sys.getsizeof(nested)
    dataset_size /= (1024**3) #bytes to gbytes

    print("\t", "The full dataset (loaded in nested list) in GB is", dataset_size)

    length = len(mfcc_features)

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
            size_utt = mfcc_features[index].nbytes / (1024**3)
            if allocated_mem + size_utt < mem_limit:
                allocated_mem += size_utt
                sampled_indices.append(index)
            else:
                break
    print("\t", "Total used memory", allocated_mem)

    return sampled_indices

def get_samples(mfcc_features, dataset_manifest, indices):
    new_manifest = list()
    lengths = list()

    for index in indices:
        new_manifest.append(dataset_manifest[index])
        lengths.append(len(mfcc_features[index]))
    
    #flatten mfcc_features
    new_mfcc_features = np.concatenate(
        [mfcc_features[index] for index in indices], axis=0
    )
    return new_mfcc_features, lengths, new_manifest

def sample_with_mem_target(mfcc_features, dataset_manifest, dataset_mem_proportion):
    #produces indices for sampling
    indices = produce_indices_with_mem_limit(mfcc_features, dataset_mem_proportion)

    #retrieve vectors with indices, build new manifest
    new_mfcc_flat, lengths, new_manifest  = get_samples(mfcc_features, dataset_manifest, indices)

    final_flat_size = new_mfcc_flat.nbytes / (1024**3)  #byte to GB

    #then return size
    return new_mfcc_flat, lengths, new_manifest, final_flat_size

def write_language_manifest(f_path, manifest_lists, language):
    #filter out iterations without sampled entries

    with open(f_path,"w") as output_file:
        output_file.write("/\n")
        for dataset in manifest_lists:
            for entry in manifest_lists[dataset]:
                output_file.write("\t".join([entry[0]+ entry[1], entry[2], language, dataset.split("/")[0]]) + "\n")

def write_numpy_chunk(feat_prefix, mfcc_features, lengths):
    feat_path = f"{feat_prefix}_{0}_{1}.npy"
    leng_path = f"{feat_prefix}_{0}_{1}.len"

    with NpyAppendArray(feat_path) as feat_f:
        feat_f.append(mfcc_features)

    with open(leng_path, "a") as leng_f:
        for length in lengths:
            leng_f.write(str(length) + "\n")

def remove_existing_files(output_prefix):
    #we will save features in append mode, so we need to make sure we are not duplicating data
    feat_path = output_prefix +"_0_1.npy"
    length_path = output_prefix + "_0_1.len"

    if os.path.exists(feat_path):
        os.remove(feat_path)
    
    if os.path.exists(length_path):
        os.remove(length_path)

def sample_language_datasets(features_root, language_distribution, language, dataset, upsampling_dataset, output_root, mem_target):
    #computes the amount of memory in GB from the max TARGET that language can use
    language_mem_proportion = mem_target*language_distribution[language]
    
    #load the datasets
    datasets = load_datasets(dataset, language)

    #define numpy where we will dump everything
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

        #loads mfcc features and manifest
        mfcc_path = features_root + dataset_root + ".checked-feats"
        mfcc_features = load_feature(mfcc_path)

        dataset_manifest = read_manifest(features_root + dataset_root + ".tsv")

        assert len(mfcc_features) == len(dataset_manifest)

        #get memory chunk dedicated for this dataset
        dataset_mem_proportion = language_mem_proportion*datasets_distribution[sub_dataset]
        print("\t", "The", sub_dataset, "mem proportion:", dataset_mem_proportion)

        #sample and write new numpy files
        new_mfcc_flat, lengths, new_manifest, dump_size = sample_with_mem_target(mfcc_features, dataset_manifest, dataset_mem_proportion)

        assert dump_size < dataset_mem_proportion

        manifests[sub_dataset] = new_manifest

        required_mem += dump_size
        print("\t", "Writing numpy chunk at", feat_path)
        write_numpy_chunk(feat_path, new_mfcc_flat, lengths)
        print("\n")
        #write numpy
    assert required_mem < language_mem_proportion

    print("\t", "Writing", output_root + "/manifest/" + language +".tsv")
    write_language_manifest(output_root + "/manifest/"+ language +".tsv", manifests, language)

if __name__ == '__main__':
    features_root=sys.argv[1]
    output_root=sys.argv[2]
    language=sys.argv[3]
    upsampling_language = float(sys.argv[4])
    upsampling_dataset = float(sys.argv[5]) 
    mem_target=float(sys.argv[6])

    dataset = utils.load_json(stats_json)
    
    #computes the language distribution with upsampling factor
    language_distribution = generate_probability_distribution(dataset, upsampling_language)
    if len(language) == 1: 
        #character case
        languages_subset = [key for key in dataset if key[0] == language]
        for language in languages_subset:
            sample_language_datasets(features_root, language_distribution, language, dataset, upsampling_dataset, output_root, mem_target)

    else:
        sample_language_datasets(features_root, language_distribution, language, dataset, upsampling_dataset, output_root, mem_target)

        