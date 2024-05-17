#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

This scripts filters entries outside range [2,30]
"""

import sys
import utils

MIN = 2
MAX = 30

def fix_filtered(data):
    for element in data:
        data[element]["audio"] = "clips/" + data[element]["audio"].replace(".mp3",".wav")
    return data

if __name__ == '__main__':
    data = utils.load_json(sys.argv[1])
    file_name = sys.argv[1].split("/")[-1]
    short = dict()
    to_remove = dict()
    filtered = dict()
    for element in data:
        if data[element]["duration"] < MIN or data[element]["duration"] > MAX:
            if data[element]["duration"] < MIN:
                short[element] = data[element]
            else:
                to_remove[element] = data[element]
        else:
            data[element]["transcription"] = data[element]["transcription"].replace("{","").replace("}","")
            data[element]["translation"] = data[element]["translation"].replace("{","").replace("}","")
            if not "[TO REMOVE]" in data[element]["translation"]:
                filtered[element] = data[element]
    

    filtered = fix_filtered(filtered)
    utils.write_json(sys.argv[1].replace(file_name,"filtered_" + file_name), filtered)

    if len(short) > 0:
        utils.write_json(sys.argv[1].replace(file_name,"short_waves.json"), short)
    
    if len(to_remove) > 0:
        with open(sys.argv[1].replace(file_name,"to_remove_list"), "w") as output_file:
            for element in to_remove:
                output_file.write(to_remove[element]["audio"] + "\n")

