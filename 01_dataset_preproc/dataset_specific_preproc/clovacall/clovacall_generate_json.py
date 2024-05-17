#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import utils

PUNCTUATION = [".",",",":",";","!","?","-", "\"", "\'"]

def remove_punctuation(sentence):
    for symbol in PUNCTUATION:
        sentence = sentence.replace(symbol,"")
    return sentence

if __name__ == '__main__':
    data = utils.load_json(sys.argv[1])
    data_test = utils.load_json(sys.argv[2])
    clova = dict()
    tokens = list()
    for element in data:
        utterance_id = element['wav'].replace(".wav","")
        clova[utterance_id] = dict()
        clova[utterance_id]["audio"] = "wavs_train/" + element['wav']
        clova[utterance_id]["duration"] = utils.load_wav(clova[utterance_id]["audio"]).duration_seconds
        clova[utterance_id]["speaker_id"] =  element['speaker_id']
        clova[utterance_id]["transcription"] = element['text']
        clova[utterance_id]["gender"] = "U"

        for token in remove_punctuation(element['text']).split(" "):
            tokens.append(token)

    for element in data_test:
        utterance_id = element['wav'].replace(".wav","")
        clova[utterance_id] = dict()
        clova[utterance_id]["audio"] = "wavs_train/" + element['wav']
        clova[utterance_id]["duration"] = utils.load_wav(clova[utterance_id]["audio"]).duration_seconds
        clova[utterance_id]["speaker_id"] =  element['speaker_id']
        clova[utterance_id]["transcription"] = element['text']
        clova[utterance_id]["gender"] = "U"

        for token in remove_punctuation(element['text']).split(" "):
            tokens.append(token)
    
    utils.write_json(sys.argv[3], clova)
    
