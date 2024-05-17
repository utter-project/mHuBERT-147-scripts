#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import glob
import utils

def read_speaker_file(f_path):
    speakers_file = [line.strip().split("\t") for line in open(f_path)][3:]
    speakers_dict = dict()
    for line in speakers_file:
        speaker_id = line[0]
        speakers_dict[speaker_id] = dict()
        if line[1] == "A":
            speakers_dict[speaker_id]["age"] = "< 14"
        elif line[1] == "B":
            speakers_dict[speaker_id]["age"] = "14-25"
        elif line[1] == "C":
            speakers_dict[speaker_id]["age"] = "26-40"
        else:
            speakers_dict[speaker_id]["age"] = "> 41"

        speakers_dict[speaker_id]["gender"] = line[2]
        speakers_dict[speaker_id]["accent"] = line[3]
    return speakers_dict

if __name__ == '__main__':
    speakers_dict = read_speaker_file(sys.argv[2])
    wav_files = glob.glob(sys.argv[1] + "/*.wav")

    dictionary = dict()
    for wav_file in wav_files:
        utt_id = wav_file.split("/")[-1].replace(".wav","")
        speaker_id = utt_id[:7]
        dictionary[utt_id] = dict()
        dictionary[utt_id]["audio"] = wav_file
        dictionary[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        dictionary[utt_id]["gender"] = speakers_dict[speaker_id]["gender"]
        dictionary[utt_id]["accent"] = speakers_dict[speaker_id]["accent"]
        dictionary[utt_id]["age"] = speakers_dict[speaker_id]["age"]
        dictionary[utt_id]["speaker_id"] = speaker_id
    utils.write_json("train.json",dictionary)