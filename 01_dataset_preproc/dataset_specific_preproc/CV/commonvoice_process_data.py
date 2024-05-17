#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""

import sys
import os 
import subprocess
from utils import write_json
from pydub import AudioSegment

def get_audio_files(tsv_path):
    files = list()
    lines = [line.strip() for line in open(tsv_path)][1:] #removes header
    for entry in lines:
        info = entry.split("\t")
        file_id = info[1]
        files.append(file_id)
    return files
        
def remove_invalid(audios_list, audio_folder):
    for entry in audios_list:
        try:
            os.remove(audio_folder + entry)
        except FileNotFoundError:
            pass

def move_audio_files(audio_list, audio_folder, audio_output_folder):
    for audio_file in audio_files:
        os.rename(audio_folder + audio_file, audio_output_folder + audio_file)

def get_duration(mp3_path):
    mp3_file = AudioSegment.from_file(file=mp3_path)
    return mp3_file.duration_seconds

def load_audio_dict(tsv_path, audio_folder, excluded):
    corpus = dict()
    tsv_content = [line.strip().split("\t") for line in open(tsv_path)][1:]
    for slices in tsv_content:
        if not slices[1] in excluded:
            audio_id = slices[1].replace(".mp3","")
            corpus[audio_id] = dict()
            corpus[audio_id]["speaker_id"] = slices[0]
            corpus[audio_id]["audio"] = slices[1]
            corpus[audio_id]["duration"] = get_duration(audio_folder + corpus[audio_id]["audio"])
            corpus[audio_id]["transcription"] = slices[2]
            corpus[audio_id]["age"] = slices[5] if slices[5] != "" else 'U'
            corpus[audio_id]["gender"] = slices[6] if slices[6] != "" else "U"
            corpus[audio_id]["accent"] = slices[7] if slices[6] != "" else "U"
    return corpus     

if __name__ == '__main__':
    #root folder at a format like cv-corpus-11.0-2022-09-21/<lang name>/
    root_folder = sys.argv[1]
    output_folder = sys.argv[2]

    # 1. remove audio files on other.tsv and invalidated.tsv

    audio_folder = root_folder + "/clips/"
    for file_name in ["/invalidated.tsv", "/other.tsv"]:
        invalid_audios = get_audio_files(root_folder + file_name)
        print("Removing", len(invalid_audios), "files")
        remove_invalid(invalid_audios, audio_folder)

    # 2. remove dev and test files to a different folder, generate a tar.gz and then remove the folder

    dev_folder = output_folder + "/dev+test/"
    if not os.path.isdir(dev_folder):
        os.mkdir(dev_folder)

    dev_test_examples = []
    for file_name in ["/dev.tsv", "/test.tsv"]:
        audio_files = get_audio_files(root_folder + file_name)
        dev_test_examples += audio_files
        print("Moving", len(audio_files), "to dev+test/")
        move_audio_files(audio_files, audio_folder, dev_folder)
    
    #if not empty
    if dev_test_examples:
        subprocess.call(['tar', '-C', dev_folder, '-czf',  output_folder + "/dev+test.tar.gz", "."])

    subprocess.call(['rm', '--dir', '-r', dev_folder])

    # 3. for the remaining audio files, extract validated.tsv information, and generate dictionary, from which we will later sample
    validated_audios = load_audio_dict(root_folder + "/validated.tsv", audio_folder, dev_test_examples)
    write_json(output_folder + "/train.json", validated_audios)




