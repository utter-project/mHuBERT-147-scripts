#code modified from notebook
# https://github.com/ina-foss/inaSpeechSegmenter/blob/master/tutorials/API_Tutorial.ipynb

import sys
import glob
import os
import utils

from joblib import parallel_backend

# Load the API
from inaSpeechSegmenter import Segmenter

def get_duration_dict(my_list):
    info = dict()
    for (key, start, stop) in my_list:
        if not key in info:
            info[key] = 0
        info[key] += stop - start
    return info

def get_event_duration(my_list, key):
    info = get_duration_dict(my_list)
    if key in info:
        return info[key]
    return 0

if __name__ == '__main__':
    wav_files = glob.glob(sys.argv[1] + "/dump/*.wav")
    seg = Segmenter()
    for folder in ["not_music", "music", "noise"]:
        try:
            os.mkdir(sys.argv[1] +"/" + folder + "/")
        except FileExistsError:
            pass

    with parallel_backend('threading', n_jobs=4):
        for wav_file in wav_files:

            segmentation = seg(wav_file)

            audio = utils.load_wav(wav_file)

            utt_id = wav_file.split("/")[-1]

            if get_event_duration(segmentation, "music") > 2: #more than 2s of music
                utils.write_wav(sys.argv[1] + "/music/" + utt_id, audio)
            elif get_event_duration(segmentation, "noise") > 2 or get_event_duration(segmentation, "noEnergy") > 5: #+2s of noise or +5s of nothing
                utils.write_wav(sys.argv[1] + "/noise/" + utt_id, audio)
            else:
                utils.write_wav(sys.argv[1] + "/not_music/" + utt_id, audio)
