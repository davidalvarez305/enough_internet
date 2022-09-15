import json
from dotenv import load_dotenv
from download import download
from gmail import send_mail
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

    count = 0

    for index, video in enumerate(data):
        if "weight loss" in video['series']:
            try:
                video['body']['snippet']['title'] = select_random_title(
                    title_options, video['series'])
                get_pics(video)
                count += 1

                values_to_write = convert_to_write_values(data)
                write_values(SPREADSHEET_ID, 'Tabs!C2:C', values_to_write)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                delete_files()
        if "AskReddit" in video['series'] or "Jokes" in video['series'] or "ELI5" in video['series'] or "TIL" in video['series'] or "ShowerThoughts" in video['series'] or "TalesFromRetail" in video['series'] or "AskHistorians" in video['series'] or "LifeProTips" in video['series']:
            try:
                vids_uploaded = tts(video)
                count += vids_uploaded

                values_to_write = convert_to_write_values(data)
                write_values(SPREADSHEET_ID, 'Tabs!C2:C', values_to_write)
            except BaseException as err:
                print(f"Error: {err}")
                delete_files()
        else:
            try:
                video['body']['snippet']['title'] = select_random_title(
                    title_options, video['series'])
                download(video)
                count += 1

                values_to_write = convert_to_write_values(data)
                write_values(SPREADSHEET_ID, 'Tabs!C2:C', values_to_write)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                delete_files()

    send_mail(count)


if __name__ == "__main__":
    main()
