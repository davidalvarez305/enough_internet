import json
import youtube_dl
import random
import ssl
from urllib import request
import os
from os import listdir
import subprocess
from youtube import upload
from pathlib import Path


def download(video):
    ssl._create_default_https_context = ssl._create_unverified_context
    username = os.environ.get('P_USER')
    password = os.environ.get('P_PASSWORD')
    port = int(os.environ.get('P_PORT'))
    url = os.environ.get('P_URL')
    session_id = random.random()
    super_proxy_url = ('http://%s-country-us-session-%s:%s@%s:%d' %
                       (username, session_id, password, url, port))
    proxy_handler = request.ProxyHandler({
        'http': super_proxy_url,
        'https': super_proxy_url,
    })

    opener = request.build_opener(proxy_handler)

    print("Downloading videos...")

    source_url = video['source'] + "?limit=" + video['limit']

    resp = opener.open(source_url).read().decode("utf-8")

    posts = json.loads(resp)

    for post in posts['data']['children']:
        if post['data']['secure_media']:
            download_link = post['data']['secure_media']['reddit_video']['fallback_url']
            with youtube_dl.YoutubeDL() as ydl:
                ydl.download([download_link])

    files = listdir()

    print("Adjusting video background...")
    for file in files:
        if ".mp4" in file:
            file_name = "output_" + file
            subprocess.run(f"ffmpeg -i {file} -lavfi '[0:v]scale=ih*16/9:-1:force_original_aspect_ratio=decrease,boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\,ch)/20:chroma_power=1[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2,crop=h=iw*9/16' -vb 800K {file_name}",
                           shell=True,
                           check=True, text=True)

    produced_files = listdir()
    files_to_join = []
    for f in produced_files:
        if "output_" in f:
            files_to_join.append("file '" + f + "'")

    with open('videos.txt', 'w') as f:
        f.write('\n'.join(files_to_join))

    vid_name = video['title'].replace(" ", "_") + ".mp4"

    subprocess.run(f"ffmpeg -f concat -safe 0 -i videos.txt -c:v libx265 -vtag hvc1 -vf scale=1920:1080 -crf 20 -c:a copy {vid_name}", shell=True,
                   check=True, text=True)

    upload(vid_name, video['body'])

    os.replace(vid_name, str(Path.home()) + "/vids/" + vid_name)
    del_files = listdir()
    for df in del_files:
        if ".mp4" in df or ".txt" in df:
            os.remove(df)
