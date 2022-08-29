import json
from dotenv import load_dotenv
from download import download
from pics import get_pics


def main():
    load_dotenv()

    file = open("vids.json")
    data = json.load(file)

    for index, video in enumerate(data):
        part = video['count'] + 1
        video['body']['snippet']['title'] = video['body']['snippet']['title'] + " part " + part
        if "weight loss motivation" in video['series']:
            get_pics(video)
        else:
            download(video)
        data[index]['count'] = part
        with open("vids.json", "w") as f:
            json.dump(data, f, indent=4)


main()
