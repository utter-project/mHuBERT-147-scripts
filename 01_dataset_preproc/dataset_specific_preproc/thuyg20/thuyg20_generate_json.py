#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import glob
import utils

if __name__ == '__main__':
    wav_files = glob.glob(sys.argv[1] + "/*")
    dictionary = dict()
    for wav_file in wav_files:
        utt_id = wav_file.split("/")[-1].replace(".wav","")
        dictionary[utt_id] = dict()
        dictionary[utt_id]["audio"] = wav_file
        dictionary[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        dictionary[utt_id]["speaker_id"] = utt_id[1:4]
        dictionary[utt_id]["gender"] = utt_id[0]
    utils.write_json(sys.argv[2], dictionary)