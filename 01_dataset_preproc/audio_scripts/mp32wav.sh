#!/bin/bash


#audio folders root
root="$1"

cd $root
for f in *.mp3; 
do 
    sox -t mp3 "$f" -r 16000 -c 1 -b 16 -e signed-integer "${f%.*}.wav";
    rm "${f%.*}.mp3"
done
	
