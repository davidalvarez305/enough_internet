import json
from dotenv import load_dotenv
from download import download
from pics import get_pics
import os
from sheets import convert_sheets_values, convert_titles, convert_to_write_values, get_tabs, get_values, select_random_title, write_values
from tts import tts
from utils import delete_files


def main():
    load_dotenv()
    SPREADSHEET_ID = str(os.environ.get('SPREADSHEET_ID'))
    vids = get_values(SPREADSHEET_ID, 'Tabs!A:Z')
    data = convert_sheets_values(vids)
    title_options = convert_titles(SPREADSHEET_ID)

    for index, video in enumerate(data):
        if "weight loss" in video['series']:
            try:
                video['body']['snippet']['title'] = select_random_title(title_options, video['series'])
                get_pics(video)

                values_to_write = convert_to_write_values(data)
                write_values(SPREADSHEET_ID, 'Tabs!C2:C', values_to_write)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                delete_files()
        if "AskReddit" in video['series'] or "Jokes" in video['series']:
            try:
                tts(video)

                values_to_write = convert_to_write_values(data)
                write_values(SPREADSHEET_ID, 'Tabs!C2:C', values_to_write)
            except BaseException as err:
                print(f"Error: {err}")
                delete_files()
        else:
            try:
                video['body']['snippet']['title'] = select_random_title(title_options, video['series'])
                download(video)

                values_to_write = convert_to_write_values(data)
                write_values(SPREADSHEET_ID, 'Tabs!C2:C', values_to_write)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                delete_files()


if __name__ == "__main__":
    main()
