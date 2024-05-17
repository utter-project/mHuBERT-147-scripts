#!/bin/bash

cd <SOMETHING HERE>/VoxLingua107/
wget http://bark.phon.ioc.ee/voxlingua107/zip_urls.txt
cat zip_urls.txt |  parallel -j 4 wget --continue