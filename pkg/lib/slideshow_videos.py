import json
from random import randrange
import re
import subprocess
import os
from os import listdir
import requests
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from mutagen.mp3 import MP3
from pkg.utils.make_request import make_request
from utils.delete_files import delete_files
from utils.upload import upload
from pathlib import Path


def select_random_inspiring_song():
    files = os.listdir()

    songs = []
    for f in files:
        if "inspiring" in f:
            songs.append(f)

    random_index = randrange(len(songs))

    return songs[random_index]


def slideshow_videos(video):
    source_url = video['source'] + "?limit=" + str(video['limit'])

    resp = make_request(source_url)

    posts = json.loads(resp)

    users = []

    for post in posts['data']['children']:
        if ".jpg" in post['data']['url'] and "nsfw" not in post['data']['thumbnail']:
            img_data = requests.get(post['data']['url']).content
            img_path = post['data']['author'] + '.jpg'
            post_title = post['data']['title']

            # User Variables
            measurements = ""
            achievements = ""
            time_frame = ""

            # User Stats Regex
            m = re.search(
                r"""^[A-Z][A-Z0-9 a-z\/'"’”]+""", post_title)
            if m != None:
                measurements = m.group()

            a = re.search(r"\[([^\[\]]+)\]", post_title)
            if a != None:
                achievements = a.group().replace("&gt;", ">").replace("&lt;", "<")

            t = re.search(r"\(([^()]+)\)", post_title)
            if t != None:
                time_frame = t.group()

            # User Intro & Description
            img_text = "\n".join([measurements, achievements, time_frame])

            with open(img_path, 'wb') as handler:
                handler.write(img_data)

            # Draw Text & Stats On To Image
            with Drawing() as draw:
                with Image(filename=img_path) as image:
                    width = int(image.width / 40)
                    height = int(image.height / 1.25)
                    draw.font = 'Roboto-Bold.ttf'
                    draw.font_size = 120
                    draw.fill_color = Color('YELLOW')
                    draw.font_weight = 600
                    draw.text(width, height, img_text)
                    draw(image)
                    image.save(filename=img_path)
                    users.append(post['data']['author'])

    # Concatenate Images & Create Final Video
    num_images = 0
    for f in listdir():
        if ".jpg" in f:
            num_images += 1
    selected_song = select_random_inspiring_song()
    audio_length = MP3(selected_song).info.length
    frame_rate = num_images / audio_length
    vid_name = video['body']['snippet']['title'].replace(" ", "_") + ".mp4"

    cmd = f"cat *.jpg | ffmpeg -framerate {frame_rate} -f image2pipe -i - -i {selected_song} -acodec copy -vf scale=1080:-2 {vid_name}"
    subprocess.run(cmd, shell=True, check=True, text=True)

    try:
        desc = "Huge props to the following users: " + ", \n".join(users)
        video['body']['snippet']['description'] = desc
        upload(vid_name, video['body'])

        os.replace(vid_name, str(Path.home()) + "/vids/" + vid_name)

        delete_files()

    except BaseException as err:
        os.replace(vid_name, str(Path.home()) + "/vids/" + vid_name)
        raise Exception("Video upload failed: ", err)
