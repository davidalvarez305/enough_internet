import os
import subprocess
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException   
from selenium.webdriver.common.by import By
from mutagen.mp3 import MP3

def main():
    load_dotenv()
    options = Options()
    user_agent = str(os.environ.get('BROWSER_AGENT'))
    options.add_argument("--headless")
    # options.add_experimental_option("detach", True)
    options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    REDDIT_POST = 'https://www.reddit.com/r/AskReddit/comments/xvfk1p/whats_the_biggest_mistake_youve_watched_someone/'

    driver.get(REDDIT_POST)

    comments = driver.find_elements(By.CLASS_NAME, 'Comment')

    for index, comment in enumerate(comments):
        comment.screenshot(f"reddit_img_{index}.png")

    num_images = 0
    for f in os.listdir():
        if ".png" in f:
            num_images += 1

    selected_song = '3jazz.mp3'

    audio_length = MP3(selected_song).info.length
    frame_rate = num_images / audio_length
    vid_name = "reddit.mp4"

    cmd = f"cat *.png | ffmpeg -framerate {frame_rate} -f image2pipe -i - -i '3jazz.mp3' -acodec copy -vf scale=1080:-2 {vid_name}"
    subprocess.run(cmd, shell=True, check=True, text=True)

main()