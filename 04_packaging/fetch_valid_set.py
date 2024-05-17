#!/usr/bin/python3
"""
Author: Marcely Zanon Boito

Copyright NAVER LABS Europe 2023

"""
import sys
import glob


#manifest generated when create_valid_set.py was executed
MANIFEST_ROOT="PATH/valid/"


def read_manifest(f_path):
    return [line.strip().replace("//","/").split("\t") for line in open(f_path)][1:]

def read_labels(f_path):
    return [line for line in open(f_path)]

def find_match(line, tsvs_list):
    for i in range(len(tsvs_list)):
        tsv_list = tsvs_list[i]
        for j in range(len(tsv_list)):
            if line == tsv_list[j][0] or line == tsv_list[j][0][1:]: #zh-TW with an extra / is messing up the match
                return i, j
    print("Did not find:", line)
    raise Exception

if __name__ == '__main__':
    manifests = glob.glob(MANIFEST_ROOT +"/*.tsv")
    print(manifests)
    labeled_train_paths = glob.glob(sys.argv[1] +"/*.tsv")
    print(labeled_train_paths)
    output_folder = sys.argv[2]
    for manifest_path in manifests:
        manifest_lines = read_manifest(manifest_path)
        dataset_id = manifest_lines[0][-1]
        train_tsvs_paths = [labeled_train_path for labeled_train_path in labeled_train_paths if dataset_id in labeled_train_path]
        train_manifests = [read_manifest(labeled_train_path) for labeled_train_path in train_tsvs_paths]
        train_labels = [read_labels(labeled_train_path.replace(".tsv",".km")) for labeled_train_path in train_tsvs_paths]
        output_label_file =  manifest_path.split("/")[-1].replace(".tsv",".km")
        print("Writing labels for:", manifest_path, "at:", output_label_file)
        with open(output_folder + "/" + output_label_file, "w") as output_labels:
            for line in manifest_lines:
                path = line[0]
                manifest_index, line_index = find_match(path, train_manifests)
                label = train_labels[manifest_index][line_index]
                output_labels.write(label)

