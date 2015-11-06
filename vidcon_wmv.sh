#! /bin/bash
for f in ls `pwd`;
do
s=${f##*/}
ffmpeg -loglevel quiet -i "${f%%.*}".wmv "${s%%.*}".wav < /dev/null;
python Run_Analysis_V2.py
done &
