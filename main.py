import json
from dotenv import load_dotenv
from download import download


def main():
    load_dotenv()

    file = open("vids.json")
    data = json.load(file)

    for index, video in enumerate(data):
        part = video['count'] + 1
        video['title'] = video['title'] + " part " + part
        download(video)
        data[index]['count'] = part
        with open("vids.json", "w") as f:
            json.dump(data, f, indent=4)


main()
