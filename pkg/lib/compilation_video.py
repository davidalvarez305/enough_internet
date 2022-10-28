import json
import youtube_dl
import os
from os import listdir
import subprocess
from constants import COMPILATION_VIDEO_DIR
from utils.make_request import make_request
from pathlib import Path
from utils.upload import upload
from utils.delete_files import delete_files
from multiprocessing import Pool

def download(post):
    params = {
        'outtmpl': COMPILATION_VIDEO_DIR + f"{post.video_author}.mp4"
    }
    with youtube_dl.YoutubeDL(params) as ydl:
        ydl.download([post.download_link])

# Compilation video downloads a list of videos from Reddit and uses FFMPEG to concatenate them on a blurred background.
def compilation_video(video):
    source_url = video['source'] + "?limit=" + str(video['limit'])
    resp = make_request(source_url)
    posts = json.loads(resp)

    users = []

    # Download All Videos
    videos = []
    reddit_posts = posts['data']['children']
    for post in reddit_posts:
        if post['data']['secure_media'] and 'reddit_video' in post['data']['secure_media']:
            users.append(post['data']['author'])
            download_link = post['data']['secure_media']['reddit_video']['fallback_url']
            video_author = post['data']['author']
            users.append({ 'download_link': download_link, 'video_author': video_author })
            
    with Pool(len(videos)) as p:
        print(p.map(download, videos))

    # Add A Blurred Background to Every Video
    files = listdir(COMPILATION_VIDEO_DIR)
    for file in files:
        file_name = "output_" + file
        try:
            subprocess.run(f"ffmpeg -i {file} -lavfi '[0:v]scale=ih*16/9:-1:force_original_aspect_ratio=decrease,boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\,ch)/20:chroma_power=1[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2,crop=h=iw*9/16' -vb 800K {file_name}",
                            shell=True,
                            check=True, text=True)
        except BaseException as err:
            os.remove(file_name)
            break

    # Create List of Videos & Concatenate Them into Final Video
    produced_files = listdir(COMPILATION_VIDEO_DIR)
    files_to_join = []
    for f in produced_files:
        if "output_" in f:
            files_to_join.append("file '" + f + "'")

    videos_text_file = COMPILATION_VIDEO_DIR + 'videos.txt'
    with open(videos_text_file, 'w') as f:
        f.write('\n'.join(COMPILATION_VIDEO_DIR + files_to_join))

    vid_name = COMPILATION_VIDEO_DIR + video['body']['snippet']['title'].replace(" ", "_") + ".mp4"

    try:
        subprocess.run(f"ffmpeg -f concat -safe 0 -i {videos_text_file} -c:v libx265 -vtag hvc1 -vf scale=1920:1080 -crf 20 -c:a copy {vid_name}", shell=True,
                       check=True, text=True)

        desc = "original sauce to the following users, in order: " + ", \n".join(users)
        video['body']['snippet']['description'] = desc
        upload(vid_name, video['body'])

        delete_files(COMPILATION_VIDEO_DIR)

    except BaseException as err:
        print("Video upload failed: ", err)
    finally:
        os.replace(vid_name, str(Path.home()) + "/vids/" + vid_name)
