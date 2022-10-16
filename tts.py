import json
import os
from pathlib import Path
from random import randrange
import re
from typing import final
from screenshot_tts import screenshot_tts
from utils import create_image, create_scrolling_video, delete_files
from make_request import make_request
from praw.models import MoreComments
import praw
import subprocess
import textwrap
from voice import save
from youtube import upload
from mutagen.mp3 import MP3
import math


def create_video_title(text):
    m = re.findall(r"[a-zA-Z0-9]+", text)
    return "_".join(m) + ".mp4"


def get_video_length(video_path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", video_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)


def select_song():
    files = os.listdir()

    songs = []
    for f in files:
        if ".mp3" in f and "post" not in f and "title" not in f and "joke" not in f:
            songs.append(f)

    random_index = randrange(len(songs))

    return songs[random_index]


def create_looped_audio(audio_path, video_length):
    audio_length = MP3(audio_path).info.length
    iterations = math.ceil(video_length/audio_length)

    i = 0
    while i < iterations:
        with open("songs.txt", 'a') as f:
            f.write("file '" + audio_path + "'" + "\n")
        i += 1

    try:
        subprocess.run(
            "ffmpeg -f concat -safe 0 -i songs.txt -c copy conv_song.mp3", shell=True,
            check=True, text=True)
    except BaseException as err:
        raise Exception("Concatenation of songs failed: ", err)


def tts(video):
    count = 0

    source_url = video['source'] + "?limit=" + str(video['limit'])

    resp = make_request(source_url)

    posts = json.loads(resp)

    for post in posts['data']['children']:
        title = post['data']['title']
        mp4_video_path = create_video_title(title)

        try:
            screenshot_tts(post)
            youtube_title = ""

            if len(title) > 100:
                youtube_title = title[:85] + "..." + " - Reddit"
            else:
                youtube_title = title + " - /r/" + video['series']

            video['body']['snippet']['description'] = post['data']['title']
            video['body']['snippet']['title'] = youtube_title

            upload(mp4_video_path, video['body'])
            count += 1

            os.replace(mp4_video_path, str(Path.home()) +
                       "/vids/" + mp4_video_path)

        except BaseException:
            continue

        finally:
            os.replace(mp4_video_path, str(Path.home()) +
                       "/vids/" + mp4_video_path)
            delete_files()

    return count
