#!/bin/bash


#audio folders root
root="$1"

cd $root
for f in *.ogg; 
do 
    ffmpeg -i "$f" "${f%.*}.wav";
    rm "${f%.*}.ogg"
done
	
