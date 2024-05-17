#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import glob
import utils


if __name__ == '__main__':
    #load speakers dict
    lines = [line.strip("\n") for line in open(sys.argv[1])][1:]
    speakers_dict = dict()
    for line in lines:
        content = line.split(" ")
        speaker_id = content[0]
        speakers_dict[speaker_id] = content[1]

    #loop on speakers
    jvs = dict()
    speakers = glob.glob(sys.argv[2] + "/*")
    for speaker_folder in speakers:
        speaker_id = speaker_folder.split("/")[-1]
        wav_files = glob.glob(speaker_folder +"/wavs/*")
        for wav_file in wav_files:
            audio_id = speaker_id + "_" + wav_file.split("/")[-1].replace(".wav","")
            jvs[audio_id] = dict()
            jvs[audio_id]["audio"] = wav_file
            jvs[audio_id]["duration"] = utils.load_wav(wav_file).duration_seconds
            jvs[audio_id]["speaker_id"] = speaker_id
            jvs[audio_id]["gender"] = speakers_dict[speaker_id]
    utils.write_json("train.json", jvs)
            