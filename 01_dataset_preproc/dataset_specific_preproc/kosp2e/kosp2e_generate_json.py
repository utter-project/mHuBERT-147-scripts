#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import glob
import utils

if __name__ == '__main__':
    covid_wavs = glob.glob(sys.argv[1] + "/covid/*")
    kosp2e = dict()
    for wav_file in covid_wavs:
        utt_id = "covid_" + wav_file.replace(".wav","").split("/")[-1]
        kosp2e[utt_id] = dict()
        kosp2e[utt_id]["audio"] = wav_file
        kosp2e[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        kosp2e[utt_id]["speaker_id"] = wav_file.replace(".wav","").split("/")[-1].split("author")[1].split("_")[0]
        if "female" in wav_file:
            kosp2e[utt_id]["gender"] = "F"
        else:
            kosp2e[utt_id]["gender"] = "M"
    
    kss_wavs = glob.glob(sys.argv[1] + "kss/")
    for wav_file in kss_wavs:
        utt_id = "kss_" + wav_file.replace(".wav","").split("/")[-1]
        kosp2e[utt_id] = dict()
        kosp2e[utt_id]["audio"] = wav_file
        kosp2e[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        if "original_" in utt_id:
            kosp2e[utt_id]["speaker_id"] = "original speaker"
        else:
            kosp2e[utt_id]["speaker_id"] = "U"
        kosp2e[utt_id]["gender"] = "U"
    
    stylekqc_wavs = glob.glob(sys.argv[1] + "/stylekqc/*")
    for wav_file in stylekqc_wavs:
        utt_id = "stylekqc_" + wav_file.replace(".wav","").split("/")[-1]
        kosp2e[utt_id] = dict()
        kosp2e[utt_id]["audio"] = wav_file
        kosp2e[utt_id]["duration"] = utils.load_wav(wav_file).duration_seconds
        kosp2e[utt_id]["speaker_id"] = "U"
        kosp2e[utt_id]["gender"] = "U"


    utils.write_json(sys.argv[2], kosp2e)
