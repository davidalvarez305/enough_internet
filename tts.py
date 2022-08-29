import json
from lib2to3.pytree import Base
import os
from gtts import gTTS
from dotenv import load_dotenv
from make_request import make_request
from praw.models import MoreComments
import praw
import subprocess
from mutagen.mp3 import MP3


def tts():
    load_dotenv()

    reddit = praw.Reddit(
        client_id=str(os.environ.get('REDDIT_ID')),
        client_secret=str(os.environ.get('REDDIT_SECRET')),
        password=str(os.environ.get('REDDIT_PASSWORD')),
        user_agent=str(os.environ.get('USER_AGENT')),
        username=str(os.environ.get('REDDIT_USERNAME')),
    )

    source_url = "https://www.reddit.com/r/AskReddit/top/.json?limit=1"

    resp = make_request(source_url)

    posts = json.loads(resp)

    title = posts['data']['children'][0]['data']['title']

    comments = []

    for post in posts['data']['children']:
        print('url: ', post['data']['url'])
        sub = reddit.submission(url=post['data']['url'])

        highest_comment_score = 0
        for index, top_level_comment in enumerate(sub.comments):
            if isinstance(top_level_comment, MoreComments):
                continue
            if index == 0:
                highest_comment_score = top_level_comment.score
            if top_level_comment.score >= highest_comment_score * 0.05:
                comment = {}
                comment['body'] = top_level_comment.body
                comment['score'] = top_level_comment.score
                audio_file = gTTS(top_level_comment.body)
                audio_path = "post" + str(index) + ".mp3"
                video_output = "post" + str(index) + ".mp4"
                audio_file.save(audio_path)
                audio_length = MP3(audio_path).info.length
                try:
                    subprocess.run(
                        f"""ffmpeg -y -f lavfi -i color=size=1920x1080:duration={audio_length}:rate=25:color=cyan \
                        -i {audio_path} -acodec copy \
                        -vf "drawtext=fontfile=Roboto-Bold.ttf:fontsize=80:fontcolor=black:x=(w-text_w)/2:y=(h-text_h)/2:text={top_level_comment.body}" \
                        {video_output}""", shell=True, check=True, text=True)
                    comments.append(comment)
                except BaseException as err:
                    print(err)


tts()
