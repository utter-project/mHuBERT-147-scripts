#!/bin/bash


#audio folders root
source=$1

for spk in $source/*;
do
    mkdir $spk/wavs/
    for wav_file in $spk/*/wav24kHz16bit/*;
    do
            sox "$wav_file" -r 16000 -c 1 -b 16 -e signed-integer "$spk/wavs/$(basename $wav_file)";	
    done
done


