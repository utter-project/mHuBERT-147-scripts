#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""
from pydub import AudioSegment

import json

def load_textgrid(file_path):
    tg = tgio.openTextgrid(file_path)
    return tg

def load_wav(file_path):
    return AudioSegment.from_wav(file_path)

def slice_wav(start, end, audio):
    start *= 1000 #s -> ms
    end *= 1000
    return audio[start:end]

def write_wav(file_name, audio):
    audio = audio.set_frame_rate(16000)
    return audio.export(file_name,format="wav")

def create_json_entry(wav_file_path, transcription, duration, speaker_id, speaker_gender):
    d = dict()
    d["path"] = wav_file_path
    d["trans"] = transcription
    d["duration"] = duration
    d["spk_id"] = speaker_id
    d["spk_gender"] = speaker_gender
    return d

def write_json_entry(output_folder, json_file_name, s_id, new_entry):
    try:
        with open(json_file_name) as json_file:
            json_data = json.load(json_file)
    except FileNotFoundError:
        json_data = dict()
    json_data[s_id] = new_entry
    with open(output_folder + "/" + json_file_name, mode='a', encoding='utf-8') as output_file:
        json.dump(json_data, output_file, ensure_ascii=False, indent=2, separators=(',', ': '))

def load_json(json_file_name):
    with open(json_file_name) as json_file:
        json_data = json.load(json_file)
    return json_data

def write_json(json_file_name, json_data, mode="w"):
    with open(json_file_name, mode=mode, encoding='utf-8') as output_file:
        json.dump(json_data, output_file, ensure_ascii=False, indent=2, separators=(',', ': '))
