#!/usr/bin/python3
"""
Author: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

1. Dataset specific processing for (dataset, language) produces train.json containing list of trainable utterances
(see 01_dataset_preproc)

-> THIS SCRIPT: 2. Dataset-level json is created by aggregating stats for all languages, manifest files are created

3. General statistics json file is created by aggregating dataset jsons
(see generate_mhubert_stats.py)
"""
import sys
import glob
import utils

PATH = "PATH/"

def generate_manifest(data, root_folder, lang):
    manifest_lines = list()
    for element in data:
        if data[element]["duration"] > 2 and data[element]["duration"] <= 30:
            try:
                path = root_folder + "/" + lang + "/" + data[element]["audio"]
            except KeyError:
                path = root_folder + "/" +  lang + "/" + data[element]["path"]
            frames = int(data[element]["duration"] * 16000)
            string = path + "\t" + str(frames) + "\n"
            manifest_lines.append(string)
    return manifest_lines

def write_manifest(manifest, file_name, root_folder):
    with open(file_name, "w") as output_file:
        output_file.write(root_folder + "\n")
        for line in manifest:
            output_file.write(line)

def get_duration(data):
    acc = 0.0
    for element in data:
        if data[element]["duration"] > 2 and data[element]["duration"] <= 30:
            acc += data[element]["duration"]
    acc = acc / 3600
    return acc

if __name__ == '__main__':
    root_folder = sys.argv[1]
    folders = glob.glob(root_folder + "/*")
    
    stats = dict()
    for folder in folders:
        lang = folder.split("/")[-1]
        print(lang)
        json_path = folder + "/concat_train.json"
        try:
            data = utils.load_json(json_path)
        except FileNotFoundError:
            try:
                json_path = folder + "/filtered_train.json"
                data = utils.load_json(json_path)
            except FileNotFoundError:
                json_path = folder + "/train.json"
                data = utils.load_json(json_path)
        stats[lang] = dict()
        stats[lang]["json"] = json_path
        stats[lang]["duration"] = get_duration(data)
        manifest = generate_manifest(data, root_folder, lang)
        write_manifest(manifest, root_folder + "/" + lang + ".tsv", PATH)

    utils.write_json(sys.argv[2], stats)
        

