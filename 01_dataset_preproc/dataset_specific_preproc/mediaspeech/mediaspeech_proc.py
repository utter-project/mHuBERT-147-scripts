#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import glob
import utils


if __name__ == '__main__':
    wav_files = glob.glob(sys.argv[1]+ "/*.wav")
    mediaspeech = dict()
    for wav_file in wav_files:
        utt_id = wav_file.split("/")[-1].replace(".wav","")
        mediaspeech[utt_id] = dict()
        mediaspeech[utt_id]["audio"] = wav_file
        mediaspeech[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        mediaspeech[utt_id]["speaker_id"] = "U"
        mediaspeech[utt_id]["gender"] = "U"
    utils.write_json("train.json", mediaspeech) 