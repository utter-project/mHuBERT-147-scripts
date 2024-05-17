#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import glob
import utils


def version1():
    wav_files = glob.glob(sys.argv[1] + "/*.wav")
    language_dict = dict()
    for wav_file in wav_files:
        utt_id = wav_file.split("/")[-1].replace(".wav","")
        language_dict[utt_id] = dict()
        language_dict[utt_id]["audio"] = wav_file
        language_dict[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        language_dict[utt_id]["gender"] = "U"
        language_dict[utt_id]["speaker_id"] = "U"
    utils.write_json("train.json", language_dict)

def version2():
    wav_files = glob.glob(sys.argv[1] + "/wavs_female/*.wav")
    language_dict = dict()
    for wav_file in wav_files:
        utt_id = wav_file.split("/")[-1].replace(".wav","")
        language_dict[utt_id] = dict()
        language_dict[utt_id]["audio"] = wav_file
        language_dict[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        language_dict[utt_id]["gender"] = "F"
        language_dict[utt_id]["speaker_id"] = "U"

    wav_files = glob.glob(sys.argv[1] + "/wavs_male/*.wav")
    for wav_file in wav_files:
        utt_id = wav_file.split("/")[-1].replace(".wav","")
        language_dict[utt_id] = dict()
        language_dict[utt_id]["audio"] = wav_file
        language_dict[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        language_dict[utt_id]["gender"] = "M"
        language_dict[utt_id]["speaker_id"] = "U"
    utils.write_json("train.json", language_dict)
    


if __name__ == '__main__':
    version1()
    #version2() #it depends on the language!
    
    

