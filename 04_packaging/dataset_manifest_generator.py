#!/usr/bin/python3
"""
Author: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""
import sys
import glob
import os

def read_manifest(manifest_path):
    return [line.strip().split("\t") for line in open(manifest_path)]

def read_label_file(labels_path):
    return [line for line in open(labels_path)]

def read_labels(labels_prefix, length):
    cat_labels = list()
    for i in range(length):
        cat_labels += read_label_file(labels_prefix + "_" + str(i) + "_" + str(length) + ".km")
        print(labels_prefix + "_" + str(i) + "_" + str(length) + ".km")
    return cat_labels

def generate_output_file(output_folder, dataset_id):
    file_dataset_id = dataset_id
    i = 0
    output_manifest_path = output_folder + "/" + file_dataset_id + ".tsv"
    print("Trying to save as", output_manifest_path)
    while os.path.isfile(output_manifest_path):
        i+=1
        file_dataset_id  = dataset_id + "_" + str(i)
        output_manifest_path = output_folder + "/" + file_dataset_id + ".tsv"
        print("It already exists, trying this instead:", output_manifest_path)
    return output_manifest_path

if __name__ == '__main__':
    manifest_folder = sys.argv[1]
    label_folder = sys.argv[2]

    output_folder = sys.argv[3]

    if len(sys.argv) > 4:
        dataset_id = sys.argv[4]
    else:
        dataset_id = manifest_folder.split("/")[-1]

    manifests_path = glob.glob(manifest_folder + "/*tsv")

    manifests = list()
    labels = list()
    languages = list()

    for manifest_path in manifests_path:
        manifests.append(read_manifest(manifest_path))
        labels_prefix = label_folder + "/" + manifest_path.split("/")[-1].replace(".tsv","")
        labels_path = glob.glob(labels_prefix + "*.km")
        labels.append(read_labels(labels_prefix, len(labels_path)))
        
        print("manifest length:", len(manifests[-1]), "labels length:", len(labels[-1]) + 1)
        assert len(manifests[-1]) == len(labels[-1]) + 1

        language = manifest_path.split("/")[-1].split(".")[0]
        languages.append(language)
    
    output_manifest_path = generate_output_file(output_folder, dataset_id)

    with open(output_manifest_path, "w") as output_manifest:
        with open(output_manifest_path.replace(".tsv",".km"),"w") as output_labels:
            try:
                output_manifest.write(manifests[0][0][0] + "\n")
            except:
                print(manifests)
                print(manifests_path)
                print(manifest_folder)
                exit(1)
            for i in range(len(manifests)):
                manifest_no_header = manifests[i][1:]
                assert len(manifest_no_header) == len(labels[i])
                for j in range(len(manifest_no_header)):
                    output_manifest.write("\t".join(manifest_no_header[j] + [languages[i], dataset_id]) + "\n")
                    output_labels.write(labels[i][j])


    frames = 0
    print(dataset_id)
    for i in range(len(manifests)):
        print(languages[i], len(labels[i]), len(manifests[i]))
        no_header = manifests[i][1:]
        frames += sum([int(no_header[j][1]) for j in range(len(no_header))])

    print("Dataset total files:", sum([len(labels[i]) for i in range(len(labels))]))
    print("Dataset total frames:", frames)
    print("Dataset languages:", len(languages))