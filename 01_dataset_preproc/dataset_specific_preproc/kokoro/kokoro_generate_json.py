#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import utils
import glob


if __name__ == "__main__":
    wav_files = glob.glob(sys.argv[1] + "/*")
    kokoro = dict()
    for wav_file in wav_files:
        file_id = wav_file.replace(".wav","").split("/")[-1]
        kokoro[file_id] = dict()
        kokoro[file_id]["audio"] = wav_file
        kokoro[file_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        kokoro[file_id]["speaker_id"] = "U"
        kokoro[file_id]["gender"] = "U"
    
    utils.write_json(sys.argv[2], kokoro)



        