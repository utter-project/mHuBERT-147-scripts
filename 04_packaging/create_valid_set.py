#!/usr/bin/python3
"""
Author: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""
import sys, glob
import random

random.seed(10)

km_suffix = "_0_1.km"

#number of instances per (language, dataset)
DEFAULT_NUMBER = 5
MANIFEST_ROOT= "PATH"
EN_MANIFEST_ROOT = "PATH" #MLS en was in a different scratch

dictionary_names = { 
            "Aishell-3": "aishell3", 
            "Aishell": "aishell", 
            "bibleTTS": "bibleTTS",
            "clovacall":"clovacall",
            "commonvoice": "CV",
            "IISc-MILE":"iiscmile",
            "jvs_ver1":"jvs",
            "Kokoro":"kokoro",
            "kosp2e":"kosp2e",
            "MediaSpeech":"mediaspeech",
            "MLS": "MLS",
            "samromur":"samromur",
            "THCHS-30":"thchs30",
            "THUYG-20":"thuyg20",
            "voxlingua107": "VL",
            "voxpopuli": "VP", 
            }

def aggregate_dataset_parts(dataset_folders):
    dictionary = dict()
    for dataset in dataset_folders:
        for key in dictionary_names:
            if key in dataset:
                if not dictionary_names[key] in dictionary:
                    dictionary[dictionary_names[key]] = list()
                dictionary[dictionary_names[key]].append(dataset)
    return dictionary

def indices_random_selection(length, examples_per_manifest):
    picked = list()
    while len(picked) < examples_per_manifest:
        index = random.randint(0, length)
        if index not in picked:
            picked.append(index)
    return picked

def manifest_to_label(label_folder, folder, language_manifest):
    return label_folder + folder.split("/")[-1] + "/" + language_manifest.split("/")[-1].split(".tsv")[0] + km_suffix

def get_subset_per_language(folder, dataset, label_folder, examples_per_manifest=DEFAULT_NUMBER):
    valid_manifest = list()
    valid_labels = list()
    languages = glob.glob(folder + "/*.tsv")
    for language_manifest in languages:
        language = language_manifest.split(".")[0].split("/")[-1]
        label_file = manifest_to_label(label_folder, folder, language_manifest)
        labels = [line for line in open(label_file)]
        manifest = [line.strip() for line in open(language_manifest)][1:]
        assert len(manifest) == len(labels)
        picked = indices_random_selection(len(manifest)-1, examples_per_manifest)
        for index in picked:
            new_manifest_line = manifest[index]+"\t" + language + "\t" + dataset + "\n"
            valid_manifest.append(new_manifest_line)
            valid_labels.append(labels[index])
    return valid_manifest, valid_labels, len(languages)
    

if __name__ == '__main__':
    #HARD CODED BECAUSE THIS CODE SHOULD ONLY BE EXECUTED ONCE
    manifest_folder = "PATH"
    label_folder = "PATH" 
    output_folder = "PATH/valid/"
    dataset_folders = glob.glob(manifest_folder + "/*")
    datasets_dict = aggregate_dataset_parts(dataset_folders)

    valid_manifest = dict()
    valid_labels = dict()
    valid_duration = 0.0
    for dataset in datasets_dict:
        valid_manifest[dataset] = list()
        valid_labels[dataset] = list()
        if dataset == "MLS":
            #different behavior because we have 20 folders corresponding to the same (language, dataset)
            #MLS is split into two parts due to the different manifest roots
            
            #english part 
            english_folders = [folder for folder in datasets_dict[dataset] if "MLS_en" in folder]
            selected_folders = [english_folders[index] for index in indices_random_selection(len(english_folders), DEFAULT_NUMBER)]
            en_manifest_entries = list()
            en_label_entries = list()
            for folder in selected_folders:
                manifest_entry, label_entry, _ = get_subset_per_language(folder, dataset, label_folder, examples_per_manifest=1)
                en_manifest_entries.append(manifest_entry[0])
                en_label_entries.append(label_entry[0])

            valid_manifest[dataset + "_en"] = en_manifest_entries
            valid_labels[dataset + "_en"] = en_label_entries

            #multilingual part
            multilingual_folder = manifest_folder + "MLS"
            manifest_entries, label_entries, num_languages = get_subset_per_language(multilingual_folder, dataset, label_folder)
            
            dataset_manifest_entries = manifest_entries
            dataset_label_entries = label_entries

        else:
            dataset_manifest_entries = list()
            dataset_label_entries = list()
            for folder in datasets_dict[dataset]:
                manifest_entries, label_entries, num_languages = get_subset_per_language(folder, dataset, label_folder)
                dataset_manifest_entries += manifest_entries
                dataset_label_entries += label_entries
        
        valid_manifest[dataset] += dataset_manifest_entries
        valid_labels[dataset] += dataset_label_entries

        valid_duration += sum((float(element.strip().split("\t")[1])/16000)/3600 for element in valid_manifest[dataset])

    print("valid total duration:", valid_duration)
    for dataset in valid_manifest:
        with open(output_folder + dataset + "_valid.tsv", "w") as output_manifest:
            with open(output_folder + dataset + "_valid.km", "w") as output_labels:
                if dataset == "MLS_en":
                    output_manifest.write(EN_MANIFEST_ROOT + "\n")
                else:
                    output_manifest.write(MANIFEST_ROOT + "\n")
                for i in range(len(valid_manifest[dataset])):
                    output_manifest.write(valid_manifest[dataset][i])
                    output_labels.write(valid_labels[dataset][i])
    

                