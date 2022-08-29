import json
from dotenv import load_dotenv
from download import download
from pics import get_pics
import os


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
                del_files = os.listdir()
                for df in del_files:
                    if ".jpg" in df or ".txt" in df or ".mp4" in df:
                        os.remove(df)
        else:
            try:
                download(video)
                data[index]['count'] = part
                with open("vids.json", "w") as f:
                    json.dump(data, f, indent=4)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                del_files = os.listdir()
                for df in del_files:
                    if ".mp4" in df or ".txt" in df:
                        os.remove(df)


main()
