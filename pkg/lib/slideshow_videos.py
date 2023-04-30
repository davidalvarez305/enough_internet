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
from multiprocessing import Pool

from constants import MUSIC_DIR, SLIDESHOW_VIDEO_DIR
from ..utils.make_request import make_request
from ..utils.delete_files import delete_files
from ..utils.upload import upload

def download_and_write_image(post):
    if ".jpg" in post['data']['url'] and "nsfw" not in post['data']['thumbnail']:
        img_data = requests.get(post['data']['url']).content
        img_path = SLIDESHOW_VIDEO_DIR + post['data']['author'] + '.jpg'
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

def select_random_inspiring_song():
    files = os.listdir(MUSIC_DIR)

    songs = []
    for f in files:
        file_path = MUSIC_DIR + f
        if "inspiring" in f:
            songs.append(file_path)

    random_index = randrange(len(songs))

    return MUSIC_DIR + songs[random_index]


def slideshow_videos(video):
    source_url = video['source'] + "?limit=" + str(video['limit'])

    resp = make_request(source_url)

    posts = json.loads(resp)

    users = []

    reddit_posts = posts['data']['children']

    with Pool(len(reddit_posts)) as p:
        print(p.map(download_and_write_image, reddit_posts))
    
    for post in reddit_posts:
        users.append(post['data']['author'])
    

    # Concatenate Images & Create Final Video
    num_images = 0
    for f in listdir(SLIDESHOW_VIDEO_DIR):
        if ".jpg" in f:
            num_images += 1

    selected_song = select_random_inspiring_song()
    audio_length = MP3(selected_song).info.length
    frame_rate = num_images / audio_length
    video_output_path = SLIDESHOW_VIDEO_DIR + video['body']['snippet']['title'].replace(" ", "_") + ".mp4"

    cmd = f"cat {SLIDESHOW_VIDEO_DIR}*.jpg | ffmpeg -framerate {frame_rate} -f image2pipe -i - -i {selected_song} -acodec copy -vf scale=1080:-2 {video_output_path}"
    subprocess.run(cmd, shell=True, check=True, text=True)

    try:
        desc = "Huge props to the following users: " + ", \n".join(users)
        video['body']['snippet']['description'] = desc
        upload(video_output_path, video['body'])

        delete_files(SLIDESHOW_VIDEO_DIR)

    except BaseException as err:
        print("Video upload failed: ", err)
