#!/bin/bash
#Date: 16/12/2020
#Author: Solène Evain
#Source: https://github.com/LeBenchmark/NeurIPS2021/

#Script pour changer les fichiers flac en wav avec sox pour le corpus MLS
#Il doit se trouver à la racine du corpus, là où se trouvent les dossiers train, dev et test

#Usage: $0 subset(train, dev ou test)"""

subset=$1
ffmpeg=PATH TO FFMPEG
cd $subset/
for i in * #locuteur_ID
do
    echo $i
    cd "$i"
    for j in * #book_ID
            do
            echo $i '\t' $j
            cd "$j"
            for audio in *.flac
                do
                wav="${audio%.*}.wav"
                name=$(basename $audio .flac)
                # '\t \t'$audio
                $ffmpeg -i $audio $wav
                #echo rm $audio
                #sox $audio -r 16k -e signed-integer -b 16 -c 1 $wav
                done
            cd ..
            done
        cd ..
done

