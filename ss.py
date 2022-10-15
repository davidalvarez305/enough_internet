import os
from re import sub
import subprocess
from typing import List
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.common.by import By
from mutagen.mp3 import MP3
from wand.image import Image
from utils import create_scrolling_video
from voice import save

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


def main():
    load_dotenv()
    options = Options()
    user_agent = str(os.environ.get('BROWSER_AGENT'))
    options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    # Original Comment: padding-left 16px
    # First reply: padding-left: 37px
    # Second reply: padding-left: 58px

    REDDIT_POST = 'https://www.reddit.com/r/AskReddit/comments/y2uefy/what_is_the_worst_thing_about_being_skinny/'

    driver.get(REDDIT_POST)

    comments = driver.find_elements(By.CLASS_NAME, 'Comment')

    # Retrieve Conversations From Reddit
    conversations = []
    sub_comments = []
    last_style = "16px"
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
            current_comment['user'] = comment.find_element(By.XPATH, './/a[@data-testid="comment_author_link"]').get_attribute('innerText')
            current_comment['image'] = ''

            sub_comments.append(current_comment)

            last_style = parent_div_style
        except NoSuchElementException:
            continue

    # Create A Video for Each Conversation
    for conv_id, conv in enumerate(conversations):
        create_conversation_video(comments=conv, conversation_id=conv_id)

main()