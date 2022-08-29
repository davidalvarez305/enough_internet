import json
import random
import re
import ssl
import subprocess
from urllib import request
import os
from os import listdir
import requests
from dotenv import load_dotenv
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color


def get_pics():
    load_dotenv()
    ssl._create_default_https_context = ssl._create_unverified_context
    username = os.environ.get('P_USER')
    password = os.environ.get('P_PASSWORD')
    port = int(os.environ.get('P_PORT'))
    url = os.environ.get('P_URL')
    session_id = random.random()
    super_proxy_url = ('http://%s-country-us-session-%s:%s@%s:%d' %
                       (username, session_id, password, url, port))
    proxy_handler = request.ProxyHandler({
        'http': super_proxy_url,
        'https': super_proxy_url,
    })

    opener = request.build_opener(proxy_handler)

    source_url = "https://www.reddit.com/r/progresspics/top/.json?limit=25"

    resp = opener.open(source_url).read().decode("utf-8")

    posts = json.loads(resp)

    for post in posts['data']['children']:
        if ".jpg" in post['data']['url'] and "nsfw" not in post['data']['thumbnail']:
            img_data = requests.get(post['data']['url']).content
            img_path = post['data']['author'] + '.jpg'
            post_title = post['data']['title']
            measurements = ""
            achievements = ""
            time_frame = ""

            m = re.search(
                r"""^[A-Z][A-Z0-9 a-z\/'"’”]+""", post_title)
            if m != None:
                measurements = m.group()

            a = re.search(r"\[([^\[\]]+)\]", post_title)
            if a != None:
                achievements = a.group().replace("&gt;", ">").replace("&lt;", "<")

            t = re.search(r"\(([^()]+)\)", post_title)
            if t != None:
                time_frame = t.group()

            img_text = "\n".join([measurements, achievements, time_frame])

            with open(img_path, 'wb') as handler:
                handler.write(img_data)

            with Drawing() as draw:
                with Image(filename=img_path) as image:
                    width = int(image.width / 40)
                    height = int(image.height / 1.25)
                    draw.font = 'Roboto-Bold.ttf'
                    draw.font_size = 120
                    draw.fill_color = Color('YELLOW')
                    draw.font_weight = 600
                    draw.text(width, height, img_text)
                    draw(image)
                    image.save(filename=img_path)

    cmd = 'cat *.jpg | ffmpeg -framerate 0.25 -f image2pipe -i - pics.mp4'
    subprocess.run(cmd, shell=True, check=True, text=True)

    del_files = listdir()
    for df in del_files:
        if ".jpg" in df or ".txt" in df:
            os.remove(df)
            print('yo')


get_pics()