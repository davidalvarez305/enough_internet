import json
import os
from pathlib import Path
from random import randrange
import re
from utils import create_image, create_scrolling_video, delete_files
from make_request import make_request
from praw.models import MoreComments
import praw
import subprocess
import textwrap
from voice import save
from youtube import upload
from mutagen.mp3 import MP3
import math


def create_slide(audio_length, audio_path, text_path, output_path):
    subprocess.run(
        f"""ffmpeg -y -f lavfi -i color=size=1920x1080:duration={audio_length}:rate=25:color=cyan \
        -i {audio_path} -acodec copy \
        -vf "drawtext=fontfile=Roboto-Bold.ttf:fontsize=50:fontcolor=black:x=(w-text_w)/2:y=(h-text_h)/2:textfile={text_path}" \
        {output_path}""", shell=True, check=True, text=True)


def wrap_text(text):
    if text.isupper():
        return textwrap.wrap(
            text, width=60, break_long_words=False, break_on_hyphens=True)

    else:
        return textwrap.wrap(
            text, width=115, break_long_words=False, break_on_hyphens=True)


def get_username(redditor):
    if hasattr(redditor, "name"):
        return redditor.name
    else:
        return "Deleted"


def create_video_title(text):
    m = re.findall(r"[a-zA-Z0-9]+", text)
    return "_".join(m) + ".mp4"


def get_video_length(video_path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", video_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)


def select_song():
    files = os.listdir()

    songs = []
    for f in files:
        if ".mp3" in f and "post" not in f and "title" not in f and "joke" not in f:
            songs.append(f)

    random_index = randrange(len(songs))

    return songs[random_index]


def create_looped_audio(audio_path, video_length):
    audio_length = MP3(audio_path).info.length
    iterations = math.ceil(video_length/audio_length)

    i = 0
    while i < iterations:
        with open("songs.txt", 'a') as f:
            f.write("file '" + audio_path + "'" + "\n")
        i += 1

    try:
        subprocess.run(
            "ffmpeg -f concat -safe 0 -i songs.txt -c copy post_song.mp3", shell=True,
            check=True, text=True)
    except BaseException as err:
        raise Exception("Concatenation of songs failed: ", err)

def create_video(text, post, author):
    audio_path = post + ".mp3"
    txt_path = post + ".txt"
    img_path = post + ".png"
    silent_path = post + "_silent.mp4"
    slide_path = post + ".mp4"
    final_path = post + "_final.mp4"
    
    wrapped_post = wrap_text(text)

    try:

        with open(txt_path, 'w') as f:
            f.write("\n".join(wrapped_post) + "\n" + "by /u/" + author)
        
        # Create Image
        create_image(txt_path, img_path)

        if os.path.isfile(img_path):

            # Create Audio
            save(text=text, path=audio_path)

            # Create initial single video
            create_scrolling_video(
                img_path, slide_path, silent_path, audio_path, final_path, len(text))

    except BaseException as err:
        print(err)



def tts(video):
    count = 0

    reddit = praw.Reddit(
        client_id=str(os.environ.get('REDDIT_ID')),
        client_secret=str(os.environ.get('REDDIT_SECRET')),
        password=str(os.environ.get('REDDIT_PASSWORD')),
        user_agent=str(os.environ.get('USER_AGENT')),
        username=str(os.environ.get('REDDIT_USERNAME')),
    )

    source_url = video['source'] + "?limit=" + str(video['limit'])

    resp = make_request(source_url)

    posts = json.loads(resp)

    for post in posts['data']['children']:
        users = [post['data']['author']]

        title = post['data']['title']
        create_video(text=title, post="title", author=post['data']['author'])

        original_post = post['data']['selftext']
        create_video(text=original_post, post="original_post", author=post['data']['author'])

        sub = reddit.submission(url=post['data']['url'])

        highest_comment_score = 0
        for index, top_level_comment in enumerate(sub.comments):
            if isinstance(top_level_comment, MoreComments):
                continue
            if index == 0:
                highest_comment_score = top_level_comment.score
            if top_level_comment.score >= highest_comment_score * 0.05:
                comment_author = get_username(top_level_comment.author)
                users.append(comment_author)
                create_video(text=top_level_comment.body, post="post" + str(index), author=comment_author)

        mp4_files = os.listdir()
        files_to_join = ["file 'title_final.mp4'"]
        if post['data']['subreddit'] == "Jokes":
            files_to_join.append("file 'joke_final.mp4'")
        for f in mp4_files:
            if "post" in f and "_final.mp4" in f:
                files_to_join.append("file '" + f + "'")

        with open('videos.txt', 'w') as f:
            f.write('\n'.join(files_to_join))

        mp4_video_path = create_video_title(title)

        try:
            subprocess.run(f"ffmpeg -f concat -safe 0 -i videos.txt -c:v libx265 -vtag hvc1 -vf scale=1920:1080 -crf 20 -c:a copy final.mp4", shell=True,
                           check=True, text=True)

            video_length = get_video_length("final.mp4")
            selected_song = select_song()
            create_looped_audio(selected_song, video_length)

            subprocess.run(
                f'''ffmpeg -i final.mp4 -i post_song.mp3 -c:v copy \
                -filter_complex "[0:a]aformat=fltp:44100:stereo,volume=1.25,apad[0a];[1]aformat=fltp:44100:stereo,volume=0.025[1a];[0a][1a]amerge[a]" -map 0:v -map "[a]" -ac 2 \
                {mp4_video_path}''', shell=True, check=True, text=True)
        except BaseException as err:
            delete_files()
            print("Video creation failed: ", err)
            continue

        try:
            desc = "OC by these users: " + ", ".join(users)
            youtube_title = ""

            if len(title) > 100:
                youtube_title = title[:85] + "..." + " - Reddit"
            else:
                youtube_title = title + " - /r/" + video['series']

            video['body']['snippet']['description'] = desc
            video['body']['snippet']['title'] = youtube_title

            upload(mp4_video_path, video['body'])
            count += 1

            os.replace(mp4_video_path, str(Path.home()) +
                       "/vids/" + mp4_video_path)

            delete_files()

        except BaseException as err:
            os.replace(mp4_video_path, str(Path.home()) +
                       "/vids/" + mp4_video_path)
            print("Request failed: ", err)
            delete_files()
            continue

    return count
