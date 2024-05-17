#!/bin/bash

DIR=$1

for lang in $DIR/*; do
  mkdir $lang/temp/
  for wav_file in $lang/speech/*; do
    ffmpeg -i $wav_file -ar 48000 -y -map_metadata -1 -flags +bitexact -acodec pcm_s16le -ac 2 $lang/temp/$(basename $wav_file)
  done
done