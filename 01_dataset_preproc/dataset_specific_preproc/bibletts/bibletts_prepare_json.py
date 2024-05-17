#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import utils
import glob


if __name__ == '__main__':
    wav_files = glob.glob(sys.argv[1] + "/*/*.wav")

    dictionary = dict()
    for wav_file in wav_files:
        utt_id = wav_file.split("/")[-1].replace(".wav","")
        dictionary[utt_id] = dict()
        dictionary[utt_id]["audio"] = wav_file
        dictionary[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        dictionary[utt_id]["gender"] = "U"
        dictionary[utt_id]["accent"] = "U"
        dictionary[utt_id]["age"] = "U"
        dictionary[utt_id]["speaker_id"] = "U"
    utils.write_json("train.json",dictionary)