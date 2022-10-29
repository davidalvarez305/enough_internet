import shutil
from dotenv import load_dotenv
from constants import COMPILATION_VIDEO_DIR, SLIDESHOW_VIDEO_DIR, TTS_VIDEO_DIR
from pkg.utils.gmail import send_mail
from pkg.lib.compilation_video import compilation_video
from pkg.lib.text_to_speech_videos import text_to_speech_videos
import os
from pkg.utils.sheets import convert_sheets_values, convert_titles, convert_to_write_values, get_values, select_random_title, write_values
from pkg.utils.delete_files import delete_files
from pkg.lib.slideshow_videos import slideshow_videos


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
                slideshow_videos(video)
                count += 1

                values_to_write = convert_to_write_values(data)
                write_values(SPREADSHEET_ID, 'Tabs!C2:C', values_to_write)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                delete_files(SLIDESHOW_VIDEO_DIR)

                continue
        if "internet clips" in video['series'] or "laughing uncontrollably" in video['series']:
            try:
                video['body']['snippet']['title'] = select_random_title(
                    title_options, video['series'])
                compilation_video(video)
                count += 1

                values_to_write = convert_to_write_values(data)
                write_values(SPREADSHEET_ID, 'Tabs!C2:C', values_to_write)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                delete_files(COMPILATION_VIDEO_DIR)

                continue
        else:
            try:
                vids_uploaded = text_to_speech_videos(video)
                count += vids_uploaded

                values_to_write = convert_to_write_values(data)
                write_values(SPREADSHEET_ID, 'Tabs!C2:C', values_to_write)
            except BaseException as err:
                print(f"Error: {err}")

                # Delete all created directories
                directories = os.listdir(TTS_VIDEO_DIR)
                for dir_path in directories:
                    shutil.rmtree(TTS_VIDEO_DIR + dir_path)

                continue

    send_mail(count)


if __name__ == "__main__":
    main()
