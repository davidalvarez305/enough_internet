import math
import os
from random import randrange
import re
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from mutagen.mp3 import MP3
from wand.image import Image
from constants import MUSIC_DIR
from ..utils.create_scrolling_video import create_scrolling_video
from ..utils.voice import save
from multiprocess.pool import ThreadPool


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
    songs = os.listdir(MUSIC_DIR)
    random_index = randrange(len(songs))
    return MUSIC_DIR + songs[random_index]

# Looped audio repeats a randomly selected song for the duration of the video ('video_length')
def create_looped_audio(audio_path, video_length, video_directory):
    audio_length = MP3(audio_path).info.length
    iterations = math.ceil(video_length/audio_length)
    SONGS_TEXT_PATH = video_directory + "songs.txt"
    LOOPED_SONG_PATH = video_directory + "conv_song.mp3"

    i = 0
    while i < iterations:
        with open(SONGS_TEXT_PATH, 'a') as f:
            f.write("file '" + audio_path + "'" + "\n")
        i += 1

    try:
        subprocess.run(
            f"ffmpeg -f concat -safe 0 -i {SONGS_TEXT_PATH} -c copy {LOOPED_SONG_PATH}", shell=True,
            check=True, text=True)
    except BaseException as err:
        print("Concatenation of songs failed: ", err)

# This functions take a list of screenshots of Reddit comments and stacks them vertically to form a long image.
def create_image(comments_list, image_output_path):
    first_image = comments_list[0]
    im = Image(filename=first_image['image'])
    with im as output:
        for img in comments_list[1:]:
            img_file = Image(filename=img['image'])
            output.sequence.append(img_file)
        output.smush(True, 5)
        output.save(filename=image_output_path)

# This takes a 'conversation' which is a list of Reddit comments.
# It creates a text-to-speech audio, and concatenates each audio to X length.
# It screenshots each comment, and stacks them vertically to form a long image.
# It then creates a video of the length of the text-to-speech audio and creates a scrolling animation of the image.
def create_conversation_video(conversation_id, comments):

    # Create video directory
    VIDEO_DIR = comments[0]['video_directory'] + f"{conversation_id}/"
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)

    # Conversation Variables
    conversation_text_file = VIDEO_DIR + f'conv_{conversation_id}.txt'
    image_output_path = VIDEO_DIR + f'conv_{conversation_id}.png'
    video_output_path = VIDEO_DIR + f'conv_{conversation_id}.mp4'
    audio_output_path = VIDEO_DIR + f'conv_{conversation_id}.mp3'
    silent_video_output_path = VIDEO_DIR + f'silent_conv_{conversation_id}.mp4'

    # The finalized video needs to be in the "TTS Video Directory" so that all of the 'final videos' can be concatenated.
    final_video_output_path = comments[0]['video_directory'] + f'final_conv_{conversation_id}.mp4'

    # Take Screenshot of Each Comment
    for index, current_comment in enumerate(comments):
        screenshot_path = VIDEO_DIR + f"comment_{index}_conv_{conversation_id}.png"
        current_comment['comment'].screenshot(screenshot_path)
        current_comment['image'] = screenshot_path

    # Create Stacked Image of Conversation
    create_image(comments, image_output_path)

    # Create Audio of Each Comment in Conversation
    audio_files = []
    for idx, comment in enumerate(comments):
        file_name = VIDEO_DIR + f'comment_{idx}_conv_{conversation_id}' + '.mp3'
        save(comment['text'], file_name)
        audio_files.append(file_name)

    # Concatenate Audio of All Comments
    for audio_file in audio_files:
        with open(conversation_text_file, 'a') as f:
            f.write("file '" + audio_file + "'" + "\n")

    # Create Single Scrolling Video for Conversation
    subprocess.run(
            f"ffmpeg -y -f concat -safe 0 -i {conversation_text_file} -c copy {audio_output_path}", shell=True, check=True, text=True)

    create_scrolling_video(
    image_output_path=image_output_path,
    video_output_path=video_output_path,
    silent_video_output_path=silent_video_output_path,
    audio_input_path=audio_output_path,
    final_video_output_path=final_video_output_path
    )


def screenshot_tts(post, video_directory):
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
            current_comment['video_directory'] = video_directory

            sub_comments.append(current_comment)
        except NoSuchElementException:
            continue

    # Create Title for Video
    title_video = {}
    TITLE_VID_DIR = video_directory + f"9999/"
    try:
        if not os.path.exists(TITLE_VID_DIR):
            os.makedirs(TITLE_VID_DIR)

        title_element = driver.find_element(By.XPATH, './/div[@data-testid="post-container"]')
        title_video['text'] = post['data']['title'] + post['data']['selftext']
        title_video['comment'] = title_element
        title_video['video_directory'] = video_directory
        create_conversation_video(comments=[title_video], conversation_id=9999)

        # Create A Video for Each Conversation
        with ThreadPool(len(conversations)) as p:
            print(p.starmap(create_conversation_video, [(index, comments) for index, comments  in enumerate(conversations)]))

        # Create Final Video
        files_to_join = [f"file '{video_directory}final_conv_9999.mp4'"]
        files = os.listdir(video_directory)

        for file in files:
            if "final_conv_" in file and not "9999" in file:
                file_path = video_directory + file
                files_to_join.append("file '" + file_path + "'")

        VIDEO_TEXT_FILE_PATH = video_directory  + 'videos.txt'
        with open(VIDEO_TEXT_FILE_PATH, 'w') as f:
            f.write('\n'.join(files_to_join))

        mp4_video_path = video_directory + create_video_title(post['data']['title'])
        
        FINAL_VIDEO_PATH = video_directory + "final.mp4"
        subprocess.run(f"ffmpeg -y -f concat -safe 0 -i {VIDEO_TEXT_FILE_PATH} -c:v libx265 -vtag hvc1 -vf scale=1920:1080 -crf 20 -c:a copy {FINAL_VIDEO_PATH}", shell=True,
                            check=True, text=True)

        video_length = get_video_length(FINAL_VIDEO_PATH)
        selected_song = select_song()
        create_looped_audio(selected_song, video_length, video_directory)
        LOOPED_SONG_PATH = video_directory + "conv_song.mp3"

        subprocess.run(
            f'''ffmpeg -y -i {FINAL_VIDEO_PATH} -i {LOOPED_SONG_PATH} -c:v copy \
            -filter_complex "[0:a]aformat=fltp:44100:stereo,volume=1.25,apad[0a];[1]aformat=fltp:44100:stereo,volume=0.025[1a];[0a][1a]amerge[a]" -map 0:v -map "[a]" -ac 2 \
            {mp4_video_path}''', shell=True, check=True, text=True)

        return mp4_video_path
    except BaseException as err:
        print("Err: ", err)
        raise Exception("Could not create video.")