#!/usr/bin/python3
"""
Date: 26/06/2022 - https://github.com/LeBenchmark/NeurIPS2021
Author: Marcely Zanon Boito
Usage: python3 get_json_stats.py <json file>
"""

import sys, copy
import datetime
from utils import load_json


def format_number(duration):
    hours = int(duration / 3600)
    minutes = int((duration % 3600) / 60)
    seconds = int((duration % 3600) % 60)
    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

def get_key(data, key):
    return [float(data[s_key][key]) for s_key in data]

def get_total_duration(data):
    return sum(get_key(data,"duration"))

def get_average_duration(data):
    return sum(get_key(data,"duration"))/len(data)

def get_max_duration(data):
    return max(get_key(data,"duration"))

def get_min_duration(data):
    return min(get_key(data,"duration"))

def get_over_threshold(data, threshold=30):
    count = 0.0 
    for s_key in data:
        if float(data[s_key]["duration"]) > threshold:
            count += 1
    return count

def get_durations_from_data(data):
    total_duration = str(format_number(get_total_duration(data)))
    avg_duration = str(format_number(get_average_duration(data)))
    min_duration = str(format_number(get_min_duration(data)))
    max_duration = str(format_number(get_max_duration(data)))
    return [total_duration, avg_duration, min_duration, max_duration]

def get_key_list(data, key):
    accents = [data[element][key] for element in data]
    return list(set(accents))

def key_in_dict(data, key):
    for element in data:
        return key in data[element]

def generate_empty_dict(key_list):
    dictionary = dict()
    for key in key_list:
        dictionary[key] = 0
    return dictionary

def get_key_count(data, key):
    if key_in_dict(data, key):
        key_list = get_key_list(data, key)
        dictionary = generate_empty_dict(key_list)
        for utt_id in data:
            dictionary[data[utt_id][key]] += 1
        return dictionary

def get_speakers(data):
    if key_in_dict(data, "speaker_id"):
        speakers = [data[element]["speaker_id"] for element in data]
        return list(set(speakers))
    else:
        return list(data.keys())

def get_subset(data, key, entry_type):
    data_subset = dict()
    for utt_id in data:
        if data[utt_id][key] == entry_type:
            data_subset[utt_id] = data[utt_id]
    return data_subset

def normalize_data(data):
    for element in data:
        for key in ["gender", "accent", "age"]:
            if key_in_dict(data, key):
                if len(data[element][key]) == 0:
                    data[element][key] = "U"       
                if key == "gender" and data[element][key] == "other":
                    data[element][key] = "U"
    return data

def print_stats(data):

    print("OVERVIEW")
    print("Number of utterances:", len(data))
    print("Number of speakers:", len(get_speakers(data))) 
    total_duration, avg_duration, min_duration, max_duration = get_durations_from_data(data)
    print("Utterances length summary for ALL")
    print("\t total duration:", total_duration)
    print("\t average:", avg_duration)
    print("\t min:", min_duration)
    print("\t max:", max_duration)
    print()

    info_dict = dict()
    print("OVERVIEW FOR SUBGROUPS")
    for key in ["gender", "accent", "age"]:
        if key_in_dict(data, key):
            print("KEY:", key.upper())
            info_dict[key] = get_key_count(data, key)
            entries_dict = list(info_dict[key].keys())
            print("\t",end="")
            print("# keys:", len(info_dict[key]), "\tdetails:", entries_dict)
            #if more than one speaker group
            if len(entries_dict) > 1:
                #for subgroup key, retrieve the entries and generate statistics
                for entry_type in entries_dict:
                    data_subset = get_subset(data, key, entry_type)
                    print("\t",end="")
                    print("Number of utterances:", len(data_subset))
                    print("\t",end="")
                    print("Number of speakers:", len(get_speakers(data_subset))) 
                    total_duration, avg_duration, min_duration, max_duration = get_durations_from_data(data_subset)
                    print("\t Utterances length summary for " + entry_type)
                    print("\t\t total duration:", total_duration)
                    print("\t\t average:", avg_duration)
                    print("\t\t min:", min_duration)
                    print("\t\t max:", max_duration)
    print()

def get_stats(file_name):
    data = load_json(file_name)
    n_data = normalize_data(data)
    print_stats(n_data)

if __name__ == "__main__":
    get_stats(sys.argv[1])