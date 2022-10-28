import json
import os
from pathlib import Path
from screenshot_tts import screenshot_tts
from utils import delete_files
from make_request import make_request
from upload import upload


def tts(video):
    count = 0

    source_url = video['source'] + "?limit=" + str(video['limit'])

    resp = make_request(source_url)

    posts = json.loads(resp)

    for post in posts['data']['children']:
        title = post['data']['title']
        mp4_video_path = ""

        try:
            mp4_video_path = screenshot_tts(post)
        except BaseException as err:
            print("Creating this video failed. ", err)
            continue
        finally:
            delete_files()

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
            continue
        finally:
            os.replace(mp4_video_path, str(Path.home()) +
                       "/vids/" + mp4_video_path)
            delete_files()

    return count
