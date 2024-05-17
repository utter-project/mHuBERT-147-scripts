#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import glob
import utils


if __name__ == '__main__':
    wav_files = glob.glob(sys.argv[1]+ "/audio/*/*/*.wav")
    corpus = dict()
    for wav_file in wav_files:
        utt_id = wav_file.split("/")[-1].replace(".wav","")
        corpus[utt_id] = dict()
        corpus[utt_id]["audio"] = wav_file
        corpus[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        corpus[utt_id]["speaker_id"] = "U"
        corpus[utt_id]["gender"] = "U"
    utils.write_json("train.json", corpus)