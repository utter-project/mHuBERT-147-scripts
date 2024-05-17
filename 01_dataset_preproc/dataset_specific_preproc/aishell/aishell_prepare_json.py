#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import glob
import utils


if __name__ == '__main__':
    speakers = glob.glob(sys.argv[1] + "/train/*")
    dictionary = dict()
    for speaker in speakers:
        wav_files = glob.glob(speaker + "/*.wav")
        for wav_file in wav_files:
            utt_id = wav_file.split("/")[-1].replace(".wav","")
            dictionary[utt_id] = dict()
            dictionary[utt_id]["audio"] = wav_file
            dictionary[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
            dictionary[utt_id]["gender"] = "U"
            dictionary[utt_id]["speaker_id"] = speaker.split("/")[-1]
    #print(dictionary)
    utils.write_json("train.json",dictionary)