import json
import random
import string
import youtube_dl
import os
from os import listdir
import subprocess
from constants import COMPILATION_VIDEO_DIR
from .make_request import make_request
from .upload import upload
from .delete_files import delete_files
from multiprocess.pool import ThreadPool

def handle_reddit_videos(video):
    videos = []

    source_url = video['source'] + "?limit=" + str(video['limit'])
    resp = make_request(source_url)
    posts = json.loads(resp)

    reddit_posts = posts['data']['children']

    for post in reddit_posts:
        if post['data']['secure_media'] and 'reddit_video' in post['data']['secure_media'] and "nsfw" not in post['data']['thumbnail']:
            download_link = post['data']['secure_media']['reddit_video']['fallback_url']
            videos.append({'download_link': download_link})

    return videos


def download(post):
    file_path = COMPILATION_VIDEO_DIR + \
        ''.join(random.choices(string.ascii_uppercase +
                string.digits, k=24)) + ".mp4"
    params = {
        'outtmpl': file_path
    }
    with youtube_dl.YoutubeDL(params) as ydl:
        ydl.download([post['download_link']])

# Compilation video downloads a list of videos from Reddit and uses FFMPEG to concatenate them on a blurred background.

def compilation_video(video):

    # Download All Videos
    videos = []

    if "reddit" in video['source']:
        reddit_videos = handle_reddit_videos(video)
        videos += reddit_videos

    with ThreadPool(len(videos)) as p:
        print(p.map(download, videos))

    # Add A Blurred Background to Every Video
    files = listdir(COMPILATION_VIDEO_DIR)
    for file in files:
        if ".mp4" in file:
            input_file = COMPILATION_VIDEO_DIR + file
            output_file = COMPILATION_VIDEO_DIR + "output_" + file
            try:
                subprocess.run(f"ffmpeg -y -i {input_file} -lavfi '[0:v]scale=ih*16/9:-1:force_original_aspect_ratio=decrease,boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\,ch)/20:chroma_power=1[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2,crop=h=iw*9/16' -vb 800K {output_file}",
                               shell=True,
                               check=True, text=True)
            except BaseException as err:
                os.remove(output_file)
                continue

    # Create List of Videos & Concatenate Them into Final Video
    produced_files = listdir(COMPILATION_VIDEO_DIR)
    files_to_join = []
    for f in produced_files:
        if "output_" in f:
            file_path = "file '" + COMPILATION_VIDEO_DIR + f + "'"
            files_to_join.append(file_path)

    videos_text_file = COMPILATION_VIDEO_DIR + 'videos.txt'
    with open(videos_text_file, 'w') as f:
        f.write('\n'.join(files_to_join))

    vid_name = COMPILATION_VIDEO_DIR + \
        video['body']['snippet']['title'].replace(" ", "_") + ".mp4"

    try:
        subprocess.run(f"ffmpeg -y -f concat -safe 0 -i {videos_text_file} -c:v libx265 -vtag hvc1 -vf scale=1920:1080 -crf 20 -c:a copy {vid_name}", shell=True,
                       check=True, text=True)

        desc = video['body']['snippet']['title']
        video['body']['snippet']['description'] = desc
        upload(vid_name, video['body'])

    except BaseException as err:
        print("Video upload failed: ", err)
    finally:
        delete_files(COMPILATION_VIDEO_DIR)
