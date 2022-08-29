import json
import youtube_dl
import os
from os import listdir
import subprocess
from make_request import make_request
from youtube import upload
from pathlib import Path


def download(video):
    source_url = video['source'] + "?limit=" + str(video['limit'])

    resp = make_request(source_url)

    posts = json.loads(resp)

    for post in posts['data']['children']:
        if post['data']['secure_media'] and 'reddit_video' in post['data']['secure_media']:
            download_link = post['data']['secure_media']['reddit_video']['fallback_url']
            with youtube_dl.YoutubeDL() as ydl:
                ydl.download([download_link])

    files = listdir()

    for file in files:
        if ".mp4" in file:
            file_name = "output_" + file
            try:
                subprocess.run(f"ffmpeg -i {file} -lavfi '[0:v]scale=ih*16/9:-1:force_original_aspect_ratio=decrease,boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\,ch)/20:chroma_power=1[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2,crop=h=iw*9/16' -vb 800K {file_name}",
                               shell=True,
                               check=True, text=True)
            except BaseException as err:
                print(err)
                os.remove(file_name)
                break

    produced_files = listdir()
    files_to_join = []
    for f in produced_files:
        if "output_" in f:
            files_to_join.append("file '" + f + "'")

    with open('videos.txt', 'w') as f:
        f.write('\n'.join(files_to_join))

    vid_name = video['body']['snippet']['title'].replace(" ", "_") + ".mp4"

    subprocess.run(f"ffmpeg -f concat -safe 0 -i videos.txt -c:v libx265 -vtag hvc1 -vf scale=1920:1080 -crf 20 -c:a copy {vid_name}", shell=True,
                   check=True, text=True)
    try:
        upload(vid_name, video['body'])

        os.replace(vid_name, str(Path.home()) + "/vids/" + vid_name)
        del_files = listdir()
        for df in del_files:
            if ".mp4" in df or ".txt" in df:
                os.remove(df)

    except BaseException as err:
        os.replace(vid_name, str(Path.home()) + "/vids/" + vid_name)
        raise Exception("Video upload failed: ", err)
