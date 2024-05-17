#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""


import sys
import glob
import utils

if __name__ == '__main__':
    files_2017 = glob.glob(sys.argv[1]+ "/2017/*.wav")
    files_2018 = glob.glob(sys.argv[1]+ "/2018/*.wav")
    files_2019 = glob.glob(sys.argv[1]+ "/2019/*.wav")
    files_2020 = glob.glob(sys.argv[1]+ "/2020/*.wav")

    vp = dict()
    for patch in [files_2017, files_2018, files_2019, files_2020]:
        for wav_file in patch:
            id = wav_file.split("/")[-1].split(".")[0]
            vp[id] = dict()
            vp[id]["audio"] = wav_file
            vp[id]["duration"] = utils.load_wav(wav_file).duration_seconds
            vp[id]["transcription"] = ""
            vp[id]["speaker_id"] = "U"
            vp[id]["gender"] = "U"


    utils.write_json(sys.argv[1] + "/train.json", vp)