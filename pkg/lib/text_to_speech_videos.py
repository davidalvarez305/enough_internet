from functools import partial
import json
from multiprocess import Pool
import os
from pathlib import Path
import shutil

from constants import TTS_VIDEO_DIR
from .screenshot_tts import screenshot_tts
from ..utils.delete_files import delete_files
from ..utils.make_request import make_request
from ..utils.upload import upload


def text_to_speech_videos(video):
    count = 0

    source_url = video['source'] + "?limit=" + str(video['limit'])

    resp = make_request(source_url)

    posts = json.loads(resp)

    reddit_posts = posts['data']['children']

    def create_video(index, post):
        title = post['data']['title']
        mp4_video_path = ""
        video_dir_name = TTS_VIDEO_DIR + f"video_{index}"
        mp4_video_path = screenshot_tts(post, video_dir_name + "/")

        try:
            youtube_title = ""

            if len(title) > 100:
                youtube_title = title[:85] + "..." + " - Reddit"
            else:
                youtube_title = title + " - /r/" + video['series']

            video['body']['snippet']['description'] = post['data']['title']
            video['body']['snippet']['title'] = youtube_title

            upload(mp4_video_path, video['body'])
            count += 1
        except BaseException as err:
            print(err)

            dirs = os.listdir(video_dir_name + "/")
            for dir_path in dirs:
                shutil.rmtree(video_dir_name + "/" + dir_path)
       

    with Pool(len(reddit_posts)) as p:
        print(p.starmap(create_video, [(index, post) for index, post  in enumerate(reddit_posts)]))
    

    return count
