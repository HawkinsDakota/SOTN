#! /bin/bash
for f in ls /mnt/data/Mockingbird\ Videos//2008/BRU/CS84/*Y;
do
s=${f##*/}
ffmpeg -loglevel quiet -i "${f%%.*}".wmv "${s%%.*}".wav < /dev/null;
python Run_Analysis_V2.py
done &