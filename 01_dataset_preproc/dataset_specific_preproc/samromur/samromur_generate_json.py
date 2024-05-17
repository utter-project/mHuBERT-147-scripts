#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import utils
import glob



def read_metadata(f_path):
    lines = [line.strip().split("\t") for line in open(f_path)][1:]
    dictionary = dict()
    for line in lines:
        dictionary[line[0]] = dict()
        dictionary[line[0]]["speaker_id"] = line[1]
        dictionary[line[0]]["path"] = line[2]
        dictionary[line[0]]["transcription"] = line[3]
        dictionary[line[0]]["speaker_gender"] = line[5]
        dictionary[line[0]]["speaker_age"] = line[6]
    return dictionary

if __name__ == '__main__':
    ROOT= "<SOMETHING HERE>/samromur/zips/samromur_unverified_22.07"
    path = ROOT + "/audio/"
    metadata = read_metadata(ROOT + "metadata.tsv")
    
    #id      speaker_id      filename        sentence        sentence_norm   gender  age     native_language dialect created_at      marosijo_score  released        is_valid        empty   duration        sample_rate     size    user_agent
    speakers = glob.glob(path + "*")

    samromur_data = dict()

    for speaker_folder in speakers:
        wav_files = glob.glob(speaker_folder + "/*.wav")
        for wav_file in wav_files:

            u_id = wav_file.split("/")[-1].replace(".wav","")
            small_id = u_id.split("-")[1]
            while small_id[0] == "0":
                small_id = small_id[1:]
            samromur_data[u_id] = dict()
            samromur_data[u_id]["audio"] = wav_file
            samromur_data[u_id]["duration"] = utils.load_wav(samromur_data[u_id]["audio"]).duration_seconds
            samromur_data[u_id]["speaker_id"] = metadata[small_id]["speaker_id"]
            samromur_data[u_id]["gender"] = metadata[small_id]["speaker_gender"]
            samromur_data[u_id]["age"] = metadata[small_id]["speaker_age"]
            samromur_data[u_id]["transcription"] = metadata[small_id]["transcription"]
    utils.write_json(sys.argv[1], samromur_data)