import json
from dotenv import load_dotenv
from download import download
from pics import get_pics
import os
from sheets import convert_sheets_values, convert_titles, get_tabs, get_values, select_random_title
from tts import tts
from utils import delete_files


def main():
    load_dotenv()
    SPREADSHEET_ID = str(os.environ.get('SPREADSHEET_ID'))
    vids = get_values(SPREADSHEET_ID, 'Tabs!A:Z')
    data = convert_sheets_values(vids)
    title_options = convert_titles(SPREADSHEET_ID)

    for index, video in enumerate(data):
        part = int(video['count']) + 1
        """ if "weight loss" in video['series']:
            try:
                video['body']['snippet']['title'] = select_random_title(title_options, video['series'])
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
                video['body']['snippet']['title'] = select_random_title(title_options, video['series'])
                download(video)
                data[index]['count'] = part
                with open("vids.json", "w") as f:
                    json.dump(data, f, indent=4)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                delete_files() """


if __name__ == "__main__":
    main()
