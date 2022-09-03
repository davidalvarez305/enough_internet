import json
from dotenv import load_dotenv
from download import download
from pics import get_pics
import os

from tts import tts
from utils import delete_files


def main():
    load_dotenv()

    file = open("vids.json")
    data = json.load(file)

    for index, video in enumerate(data):
        part = video['count'] + 1
        video['body']['snippet']['title'] = video['series'] + \
            " part " + str(part)
        if "weight loss" in video['series']:
            try:
                get_pics(video)
                data[index]['count'] = part
                with open("vids.json", "w") as f:
                    json.dump(data, f, indent=4)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                delete_files()
        if "AskReddit" in video['series'] or "Jokes" in video['series']:
            try:
                tts(video)
                data[index]['count'] = part
                with open("vids.json", "w") as f:
                    json.dump(data, f, indent=4)
            except BaseException as err:
                print(f"Error: {err}")
                delete_files()
        else:
            try:
                download(video)
                data[index]['count'] = part
                with open("vids.json", "w") as f:
                    json.dump(data, f, indent=4)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                delete_files()


if __name__ == "__main__":
    main()
