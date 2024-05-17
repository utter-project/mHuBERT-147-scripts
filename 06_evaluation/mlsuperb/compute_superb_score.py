#!/usr/bin/python3
"""
Author: Marcely Zanon Boito

Copyright NAVER LABS Europe 2024

This scripts implements ML-SUPERB scoring following https://arxiv.org/abs/2305.10615
"""

#Results extracted from findings paper + mHuBERT-147 results
string_dict = { 
    'MMS1B': "33.3 / 25.7	21.3 / 18.1	30.2 / 30.8	84.8 / 86.1	73.3 / 74.8	26.0 / 25.5	25.4 / 24.8",
    'NWHC1': "39.5 / 30.5	28.9 / 21.5	41.4 / 38.6	67.1 / 87.4	77.1 / 90.6	28.8 / 21.5	40.3 / 38.2",
    'NWHC2': "39.5 / 30.5	29.3 / 21.6	42.0 / 39.3	64.4 / 88.1	77.4 / 90.6	28.4 / 21.8	41.5 / 38.8",
    'XLS-R-128': "39.7 / 30.6	29.2 / 22.0	40.9 / 39.3	66.9 / 87.9	55.6 / 85.6	28.4 / 22.9	42.1 / 42.4",
    'MMS300M': "33.8 / 30.5	28.7 / 24.0	36.5 / 36.5	62.3 / 84.3	71.9 / 74.3	31.5 / 30.0	30.9 / 29.2",
    'WavLabLM-large-MS':"40.5 / 32.8	37.8 / 31.9	43.8 / 42.8	71.7 / 81.1	70.8 / 80.0	37.0 / 32.2	43.4 / 41.2",
    'FBANK': "72.1 / 63.7	62.4 / 59.3	58.3 / 57.4	11.1 / 9.3	35.9 / 43.5	62.0 / 58.6	58.9 / 58.1",
    'mHuBERT147-2nd': "35.9 / 27.6	25.4 / 22.5 	34.2 / 33.8	74.8 / 90.1	81.0 / 89.0	26.3 / 23.6	33.9 / 34.4",
    'mHuBERT147-3rd': "34.2 / 26.3	23.6 / 22.0	33.2 / 32.9	85.3 / 91.0	81.4 / 90.0	26.2 / 22.1	34.9 / 33.5",
    }
#from original paper
#string_dict = { 
#    'XLS-R-128': "39.7 / 30.6	29.2 / 22.0	40.9 / 39.3	66.9 / 87.9	55.6 / 85.6	28.4 / 22.9	42.1 / 42.4",
#    'FBANK': "72.1 / 63.7	62.4 / 59.3	58.3 / 57.4	11.1 / 9.3	35.9 / 43.5	62.0 / 58.6	58.9 / 58.1",
#   'HuBERT-base-cmn': "43.1 / 35.6	40.8 / 43.2	45.4 / 46.6	49.3 / 85.3	75.1 / 86.1	37.7 / 31.8	43.5 / 42.1",
#    'HuBERT-large': "38.2 / 32.2	44.4 / 37.7	48.2 / 43.5	46.5 / 64.1	55.4 / 77.7	45.6 / 35.1	49.3 / 41.8",
#    'HuBERT-base': "42.8 / 35.3	39.8 / 31.4	44.5 / 42.7	61.2 / 86.1	71.5 / 86.0	39.2 / 30.9	43.8 / 41.8",
#    }

def get_scores_from_string(string, model_name):
    slices = string.split("\t")
    for i in range(len(slices)):
        slice = slices[i]
        slice = slice.replace(" ","")
        score = slice.split("/")
        if i == 0: #first index is monolingual ASR
            task = "monolingual_asr"
        elif i == 1 or i == 2: # multilingual ASR normal setting
            task = "multilingual_asr"
        elif i == 3:
            task = "lid"
        else:
            task = "multilingual_asr_lid"
        models[model_name]['10min'][task].append(float(score[0]))
        models[model_name]['1h'][task].append(float(score[1]))

def find_sota(models):
    SOTA = dict()
    for setting in ['10min', '1h']:
            SOTA[setting] = {"monolingual_asr": [100], "multilingual_asr": [100, 100], "lid": [0], "multilingual_asr_lid": [0,100,100]}
    for model_name in models:
        for setting in ['10min', '1h']:
            # "monolingual_asr"
            task = "monolingual_asr"
            model_score = models[model_name][setting][task]
            if  model_score < SOTA[setting][task]:
                SOTA[setting][task] = model_score
            task = "multilingual_asr"
            for i in range(2):
                model_score = models[model_name][setting][task][i]
                if  model_score < SOTA[setting][task][i]:
                    SOTA[setting][task][i] = model_score
            task = "lid"
            model_score = models[model_name][setting][task]
            if  model_score > SOTA[setting][task]:
                SOTA[setting][task] = model_score
            task = "multilingual_asr_lid"
            model_score = models[model_name][setting][task][0]
            if  model_score > SOTA[setting][task][0]:
                SOTA[setting][task][0] = model_score
            for i in [1,2]:
                model_score = models[model_name][setting][task][i]
                if  model_score < SOTA[setting][task][i]:
                    SOTA[setting][task][i] = model_score
    return SOTA

def compute_superb_score(model_name, models, setting, SOTA):
    num_tasks = 4
    task = "monolingual_asr"
    task1_score_internal = (models[model_name][setting][task][0] - models['FBANK'][setting][task][0])/(SOTA[setting][task][0] - models['FBANK'][setting][task][0])
    task1_score = 1.0 / len(models[model_name][setting][task]) * task1_score_internal

    task = "multilingual_asr"
    task2_score_internal = 0.0
    for i in range(len(models[model_name][setting][task])):
        task2_score_internal += (models[model_name][setting][task][i] - models['FBANK'][setting][task][i])/(SOTA[setting][task][i] - models['FBANK'][setting][task][i])
    task2_score = 1.0 / len(models[model_name][setting][task]) * task2_score_internal

    task = "lid"
    task3_score_internal = (models[model_name][setting][task][0] - models['FBANK'][setting][task][0])/(SOTA[setting][task][0] - models['FBANK'][setting][task][0])
    task3_score = 1.0 / len(models[model_name][setting][task]) * task3_score_internal

    task = "multilingual_asr_lid"
    task4_score_internal = 0.0
    for i in range(len(models[model_name][setting][task])):
        task4_score_internal += (models[model_name][setting][task][i] - models['FBANK'][setting][task][i])/(SOTA[setting][task][i] - models['FBANK'][setting][task][i])
    task4_score = 1.0 / len(models[model_name][setting][task]) * task4_score_internal
    
    score = 1000/num_tasks * (task1_score + task2_score + task3_score + task4_score)

    return score


models = dict()

for key in string_dict:
    models[key] = dict()
    for setting in ['10min', '1h']:
        models[key][setting] = {"monolingual_asr": [], "multilingual_asr": [], "lid": [], "multilingual_asr_lid": []}
    get_scores_from_string(string_dict[key], key)

SOTA = find_sota(models)

for setting in ["10min", "1h"]:
    print(setting)
    for model in models:
        print(model, compute_superb_score(model, models, setting, SOTA))
    print()