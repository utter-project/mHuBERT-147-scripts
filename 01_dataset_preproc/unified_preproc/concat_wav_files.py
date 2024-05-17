#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

This scripts works after filter_json_files.py, concatenating short utterances
"""
import sys
import utils

MAX_DURATION = 30.0
AUDIO_FOLDER = ""
JSON_OUT_NAME = "concat_train.json"

def merge_with_existing_group(json_data, key_to_merge, dictionary, dictionary_id):
    new_entry = dict()
    if isinstance(json_data[key_to_merge]["audio"], list):
        new_entry["audio"] = json_data[key_to_merge]["audio"] + [dictionary["audio"]]
    else:
        new_entry["audio"] = [json_data[key_to_merge]["audio"], dictionary["audio"]]
    if "transcription" in json_data.keys():
        new_entry["transcription"] = json_data[key_to_merge]["transcription"] + "[concat]" + dictionary["transcription"]
    new_entry["duration"] = float(json_data[key_to_merge]["duration"]) + float(dictionary["duration"])
    new_entry["speaker_id"] = json_data[key_to_merge]["speaker_id"]
    new_entry["gender"] = json_data[key_to_merge]["gender"]
    entry_id = key_to_merge + "_" + dictionary_id
    return entry_id, new_entry

def remove_entries(entries, new_group):
    for element in new_group:
        entries.remove(element) #this works because these are unique ids

def find_group(json_data, dictionary):
    for element in json_data:
        if float(json_data[element]["duration"]) + float(dictionary["duration"]) <= MAX_DURATION:
            return element
    return None

def insert_small_entry(temp_dict, extra_json, dictionary, dictionary_id):
    key_to_merge = find_group(temp_dict, dictionary)
    if key_to_merge != None: #found possible match
        new_merged_id, new_merged_entry = merge_with_existing_group(temp_dict, key_to_merge, dictionary, dictionary_id)
        temp_dict[new_merged_id] = new_merged_entry
        del temp_dict[key_to_merge]
        return True
    #otherwise searches for a possible group in regular files
    key_to_merge = find_group(extra_json, dictionary)
    if key_to_merge != None: #found possible match
        new_merged_id, new_merged_entry = merge_with_existing_group(extra_json, key_to_merge, dictionary, dictionary_id)
        temp_dict[new_merged_id] = new_merged_entry
        del extra_json[key_to_merge]
        return True
    return False

def generate_json_entry_from_group(json_data, entries):
    new_entry = dict()
    new_entry["audio"] = list() #at this point we keep the audio for loading the audios later
    if "transcription" in json_data.keys():
        new_entry["transcription"] = list()
    new_entry["duration"] = 0.0
    #since we are fetching from the same speaker, these are identical for all entries in the batch
    new_entry["speaker_id"] = list() 
    new_entry["gender"] = list() 
    new_entry["accent"] = "U"
    new_entry["age"] = "U"
    for element in entries:
        new_entry["duration"] += float(json_data[element]["duration"])
        new_entry["audio"].append(json_data[element]["audio"])
        if "transcription" in json_data.keys():
            new_entry["transcription"].append(json_data[element]["transcription"])
        new_entry["gender"].append(json_data[element]["gender"])
        new_entry["speaker_id"].append(json_data[element]["speaker_id"])
    if "transcription" in json_data.keys():
        new_entry["transcription"] = "[concat]".join(new_entry["transcription"])
    for key in ["gender", "speaker_id"]:
        new_entry[key] = "[concat]".join(new_entry[key])

    entry_id = "_".join(entries) #create the new id as a concatenation of the ids
    return entry_id, new_entry

def group_batch(json_data, entries, duration):
    this_duration = 0.0
    new_batch = list()
    for entry in entries:
        this_duration += float(json_data[entry]["duration"])
        new_batch.append(entry)
        if this_duration >= duration:
            return new_batch, this_duration
    return new_batch, this_duration

def group_audios(json_data, extra_json, duration=10):
    entries = list(json_data.keys())
    reinsert = list()
    temp_dict = dict()
    dump_dict = dict()
    #while there are entries
    while entries and len(entries) > 0 :
        #get a batch of 10s (or less if there are any entries left)
        new_group, this_duration = group_batch(json_data, entries, duration)
        #create new id for the group
        if this_duration >= duration:
            new_id, new_entry = generate_json_entry_from_group(json_data, new_group)
            temp_dict[new_id] = new_entry
        else: #last batch will be potentially smaller
            reinsert = new_group
        #remove entries for the next iteration
        remove_entries(entries, new_group)

    #check if any of the groups is too small
    if len(reinsert) > 0: 
        for element in reinsert: 
            if not insert_small_entry(temp_dict, extra_json, json_data[element], element):
                sys.stderr.write(element + "\n")
                dump_dict[element] = copy.deepcopy(json_data[element])
    return temp_dict, dump_dict

def write_wav_files_from_json(json_data, output_folder, merging=False):
    waves_to_remove = list()
    for element in json_data:
        audio_path = json_data[element]["audio"]
        if len(element + ".wav") > 100:
            output_path = output_folder + "/" + AUDIO_FOLDER + element[:70] + ".wav"
        else:
            output_path = output_folder + "/" + AUDIO_FOLDER + element + ".wav"
        json_data[element]["audio"] = output_path
        if not merging:
            audio = utils.load_wav(audio_path)
            utils.write_wav(output_path, audio)
        else:
            audio_list = list()
            try:
                for path in audio_path: #audio path is a list
                    audio = utils.load_wav(path) #voxlingua has extra level for language id
                    audio_list.append(audio)
                audio = audio_list[0]
                for wav in audio_list[1:]:
                    audio = audio.append(wav)
                utils.write_wav(output_path, audio)
                waves_to_remove += audio_path
            except ValueError:
                #crossfade longer than segment
                pass
        json_data[element]["duration"] = audio.duration_seconds
    return json_data, waves_to_remove

def write_final_json(good_json, new_entries, output_folder):
    fixed_json, files_to_remove = write_wav_files_from_json(new_entries, output_folder, merging=True)
    good_json.update(fixed_json)
    utils.write_json(output_folder + "/" + JSON_OUT_NAME, good_json, mode="a")
    with open(output_folder + "/waves_to_remove", "w") as output_file:
        for file_id in files_to_remove:
            output_file.write(file_id + "\n")

def remove_zero(data):
    to_remove = list()
    for element in data:
        if data[element]["duration"] == 0:
            to_remove.append(element)
    for element in to_remove:
        del data[element]
    return data

if __name__ == '__main__':
    try:
        short_data = utils.load_json(sys.argv[1] + "/short_waves.json")
    except FileNotFoundError:
        sys.exit(0)
    AUDIO_FOLDER = sys.argv[2]
    data = utils.load_json(sys.argv[1] + "/filtered_train.json")
    data = remove_zero(data)
    new_entries, dump = group_audios(short_data, data, duration=2)
    write_final_json(data, new_entries, sys.argv[1])
