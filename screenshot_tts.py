import math
import os
from random import randrange
import re
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.common.by import By
from mutagen.mp3 import MP3
from wand.image import Image
from utils import create_scrolling_video, delete_files
from voice import save


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
            "ffmpeg -f concat -safe 0 -i songs.txt -c copy conv_song.mp3", shell=True,
            check=True, text=True)
    except BaseException as err:
        raise Exception("Concatenation of songs failed: ", err)

def create_image(comments_list, image_output_path):
    first_image = comments_list[0]
    im = Image(filename=first_image['image'])
    with im as output:
        for img in comments_list[1:]:
            img_file = Image(filename=img['image'])
            output.sequence.append(img_file)
        output.smush(True, 5)
        output.save(filename=image_output_path)

def create_conversation_video(comments, conversation_id: int):

    # Conversation Variables
    conversation_text_file = f"conv_{conversation_id}.txt"
    image_output_path = f'conv_{conversation_id}.png'
    video_output_path = f'conv_{conversation_id}.mp4'
    audio_output_path = f'conv_{conversation_id}.mp3'
    silent_video_output_path = f'silent_conv_{conversation_id}.mp4'
    final_video_output_path = f'final_conv_{conversation_id}.mp4'

    # Take Screenshot of Each Comment
    for index, current_comment in enumerate(comments):
        img_name = f"comment_{index}_conv_{conversation_id}.png"
        current_comment['comment'].screenshot(img_name)
        current_comment['image'] = img_name

    # Create Stacked Image of Conversation
    create_image(comments, image_output_path)

    # Create Audio of Each Comment in Conversation
    audio_files = []
    for idx, comment in enumerate(comments):
        file_name = f'comment_{idx}_conv_{conversation_id}'
        save(comment['text'], file_name + '.mp3')
        audio_files.append(file_name + '.mp3')

    # Concatenate Audio of All Comments
    for audio_file in audio_files:
        with open(conversation_text_file, 'a') as f:
            f.write("file '" + audio_file + "'" + "\n")

    # Create Single Scrolling Video for Conversation
    subprocess.run(
            f"ffmpeg -f concat -safe 0 -i {conversation_text_file} -c copy {audio_output_path}", shell=True, check=True, text=True)

    create_scrolling_video(
    image_output_path=image_output_path,
    video_output_path=video_output_path,
    silent_video_output_path=silent_video_output_path,
    audio_input_path=audio_output_path,
    final_video_output_path=final_video_output_path
    )


def screenshot_tts(post):
    options = Options()
    user_agent = str(os.environ.get('BROWSER_AGENT'))
    options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    # Original Comment: padding-left 16px
    # First reply: padding-left: 37px
    # Second reply: padding-left: 58px

    driver.get(post['data']['url'])

    comments = driver.find_elements(By.CLASS_NAME, 'Comment')

    # Retrieve Conversations From Reddit
    conversations = []
    sub_comments = []
    for index, comment in enumerate(comments):
        try:
            parent_div = comment.find_element(By.XPATH, "../../div")
            parent_div_style = parent_div.get_attribute('style')

            if "16px" in parent_div_style and not index == 0:
                conversations.append(sub_comments)
                sub_comments = []

            current_comment = {}
            current_comment['style'] = parent_div_style
            current_comment['comment'] = parent_div
            current_comment['text'] = comment.find_element(By.XPATH, './/div[@data-testid="comment"]').get_attribute('innerText')
            current_comment['image'] = ''

            sub_comments.append(current_comment)
        except NoSuchElementException:
            continue

    # Create Title for Video
    title_video = {}
    title_element = driver.find_element(By.XPATH, './/div[@data-testid="post-container"]')
    title_video['text'] = post['data']['title'] + post['data']['selftext']
    title_video['comment'] = title_element
    create_conversation_video(comments=[title_video], conversation_id=9999)

    # Create A Video for Each Conversation
    for conv_id, conv in enumerate(conversations):
        create_conversation_video(comments=conv, conversation_id=conv_id)

    # Create Final Video
    files_to_join = ["file 'final_conv_9999.mp4'"]
    files = os.listdir()
    for file in files:
            if "final_conv_" in file:
                files_to_join.append("file '" + file + "'")

    with open('videos.txt', 'w') as f:
        f.write('\n'.join(files_to_join))

    mp4_video_path = create_video_title(post['data']['title'])

    try:
        subprocess.run(f"ffmpeg -f concat -safe 0 -i videos.txt -c:v libx265 -vtag hvc1 -vf scale=1920:1080 -crf 20 -c:a copy final.mp4", shell=True,
                           check=True, text=True)

        video_length = get_video_length("final.mp4")
        selected_song = select_song()
        create_looped_audio(selected_song, video_length)

        subprocess.run(
            f'''ffmpeg -i final.mp4 -i conv_song.mp3 -c:v copy \
            -filter_complex "[0:a]aformat=fltp:44100:stereo,volume=1.25,apad[0a];[1]aformat=fltp:44100:stereo,volume=0.025[1a];[0a][1a]amerge[a]" -map 0:v -map "[a]" -ac 2 \
            {mp4_video_path}''', shell=True, check=True, text=True)
    except BaseException:
        pass
    finally:
        return mp4_video_path