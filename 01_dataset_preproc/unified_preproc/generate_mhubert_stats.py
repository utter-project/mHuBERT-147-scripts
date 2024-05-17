#!/usr/bin/python3
"""
Author: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

1. Dataset specific processing for (dataset, language) produces train.json containing list of trainable utterances
(see 01_dataset_preproc)

2. Dataset-level json is created by aggregating stats for all languages, manifest files are created
(see generate_dataset_stats.py)

-> THIS SCRIPT: 3. General statistics json file is created by aggregating dataset jsons
"""
import sys
import glob
import utils

def generate_dictionary(corpora_list):
    stats_dict = dict()
    for json_dict in corpora_list:
        for element in json_dict: #language
            if not element in stats_dict:
                stats_dict[element] = dict()
                stats_dict[element]["json"] = [json_dict[element]["json"]]
                stats_dict[element]["duration"] = json_dict[element]["duration"]
            else:
                stats_dict[element]["json"].append(json_dict[element]["json"])
                stats_dict[element]["duration"] += json_dict[element]["duration"]
    return stats_dict

def sum_duration(stats_dict):
    return sum([stats_dict[element]["duration"] for element in stats_dict])

def print_statistics(stats_dict):
    print("TOTAL DURATION:", sum_duration(stats_dict))
    print("# LANGUAGES:", len(stats_dict))


def fetch(root_folder):
    json_files = glob.glob(root_folder + "/*.json")
    corpora_list = list()
    for json_file in json_files:
        print(json_file)
        corpora_list.append(utils.load_json(json_file))
    
    stats_dict = generate_dictionary(corpora_list)
    print_statistics(stats_dict)
    
    utils.write_json(sys.argv[2], stats_dict)


if __name__ == '__main__':
    fetch(sys.argv[1])