import json
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

    for index, post in enumerate(posts['data']['children']):
        title = post['data']['title']
        mp4_video_path = ""
        video_dir_name = f"video_{index}"
        os.makedirs(video_dir_name)
        video_directory = TTS_VIDEO_DIR + video_dir_name + "/"

        try:
            mp4_video_path = screenshot_tts(post, video_directory)

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
            continue
        finally:
            os.replace(mp4_video_path, str(Path.home()) +
                       "/vids/" + mp4_video_path)

            dirs = os.listdir(video_directory)
            for dir_path in dirs:
                shutil.rmtree(dir_path)

    return count
