#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""
import utils
import sys

KEY = "audio"
json_dict = utils.load_json(sys.argv[1])
wav_list = list()
for element in json_dict:
    wav_list.append(json_dict[element][KEY])


with open(sys.argv[2],"w") as output_file:
    for line in wav_list:
        output_file.write(line + "\n")
