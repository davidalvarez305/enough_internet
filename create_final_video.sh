#!/bin/sh

SILENT_VIDEO_OUTPUT_PATH=$1
AUDIO_INPUT_PATH=$2
FINAL_VIDEO_OUTPUT_PATH=$3

ffmpeg -i $SILENT_VIDEO_OUTPUT_PATH -i $AUDIO_INPUT_PATH -c:v copy \
-filter_complex "[0:a]aformat=fltp:44100:stereo,apad[0a];[1]aformat=fltp:44100:stereo,volume=0.75[1a];[0a][1a]amerge[a]" \
-map 0:v -map "[a]" -ac 2 $FINAL_VIDEO_OUTPUT_PATH