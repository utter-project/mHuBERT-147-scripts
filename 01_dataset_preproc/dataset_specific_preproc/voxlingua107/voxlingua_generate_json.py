#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import glob
from utils import write_json, load_wav


if __name__ == '__main__':
    #/!\ Run VAD before this step
    wav_files = glob.glob(sys.argv[1] + "/not_music/*")
    output_file = sys.argv[1] + "/train.json"
    corpus = dict()
    for wav_file in wav_files:
        audio_id = wav_file.split("/")[-1][:-4]
        corpus[audio_id] = dict()
        corpus[audio_id]["speaker_id"] = audio_id.split("__U__")[1].split("--")[0]
        corpus[audio_id]["audio"] = wav_file
        corpus[audio_id]["duration"] = load_wav(wav_file).duration_seconds
        corpus[audio_id]["transcription"] = ""
        corpus[audio_id]["age"] = "U"
        corpus[audio_id]["gender"] = "U"
        corpus[audio_id]["accent"] = "U"
    
    write_json(output_file, corpus)

