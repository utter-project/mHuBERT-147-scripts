#!/usr/bin/python3
"""
Author: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""


import sys
import glob

#this script checks how many files were removed by VAD

if __name__ == '__main__':
    langs = glob.glob(sys.argv[1] + "/*")
    langs = [element for element in langs if not ".tsv" in element]
    dictionary = dict()
    for lang in langs:
        lang_key = lang.split("/")[-1]
        noise = glob.glob(lang + "/noise/*")
        music = glob.glob(lang + "/music/*")
        speech = glob.glob(lang + "/not_music/*")
        dictionary[lang_key] = dict()
        for key in ["noise", "music", "not_music"]:
            dictionary[lang_key][key] = len(glob.glob(lang + "/" + key + "/*"))
        print(lang_key, dictionary[lang_key])
    
    with open("voxlingua_loss.csv","w") as output_file:
        output_file.write(",".join(["language", "# files", "# speech","# music", "# noise"]) + "\n")
        for language in dictionary:
            count = 0
            for key in ["noise", "music", "not_music"]:
                count += dictionary[language][key]
            output_file.write(",".join([language, str(count), str(dictionary[language]["not_music"]), 
                            str(dictionary[language]["music"]), str(dictionary[language]["noise"])]) + "\n")