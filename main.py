from dotenv import load_dotenv
from gmail import send_mail
from lib.download import download
from lib.tts import tts
import os
from sheets import convert_sheets_values, convert_titles, convert_to_write_values, get_values, select_random_title, write_values
from utils.delete_files import delete_files
from lib.pics import get_pics


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
        if "internet clips" in video['series'] or "laughing uncontrollably" in video['series']:
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
        else:
            try:
                vids_uploaded = tts(video)
                count += vids_uploaded

                values_to_write = convert_to_write_values(data)
                write_values(SPREADSHEET_ID, 'Tabs!C2:C', values_to_write)
            except BaseException as err:
                print(f"Error: {err}")
                delete_files()

    send_mail(count)


if __name__ == "__main__":
    main()
