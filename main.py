import json
import youtube_dl
import random
import ssl
from urllib import request
import os
from os import listdir
import subprocess
from youtube import upload
from dotenv import load_dotenv


def main():
    load_dotenv()
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

    resp = opener.open(
        'https://www.reddit.com/r/funnyvideos/top/.json?limit=5').read().decode("utf-8")

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
            subprocess.run(f"ffmpeg -i {file} -lavfi '[0:v]scale=ih*16/9:-1,boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\,ch)/20:chroma_power=1[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2,crop=h=iw*9/16' -vb 800K {file_name}",
                           shell=True,
                           check=True, text=True)

    produced_files = listdir()
    files_to_join = []
    for f in produced_files:
        if "output_" in f:
            files_to_join.append("file '" + f + "'")

    with open('videos.txt', 'w') as f:
        f.write('\n'.join(files_to_join))

    print("Creating final video...")

    subprocess.run(f"ffmpeg -f concat -safe 0 -i videos.txt final.mp4", shell=True,
                   check=True, text=True)

    upload("final.mp4")


main()
