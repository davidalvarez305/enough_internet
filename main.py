import json
from constants import CREDENTIALS_DIR, COMPILATION_VIDEO_DIR
from pkg.utils.gmail import send_mail
from pkg.utils.compilation_video import compilation_video
from pkg.utils.sheets import convert_sheets_values, convert_to_write_values, get_values, write_values
from pkg.utils.delete_files import delete_files

def main():
    f = open(CREDENTIALS_DIR + "env.json")
    env = json.load(f)
    SPREADSHEET_ID = str(env.get('SPREADSHEET_ID'))
    vids = get_values(SPREADSHEET_ID, 'Tabs!A:D')
    data = convert_sheets_values(vids)

    count = 0

    for video in data:
        part = int(video['count']) + 1
        try:
            video['body']['snippet']['title'] = video['series'] + "Compilation - Part " + str(part)
            compilation_video(video)
            count += 1

            values_to_write = convert_to_write_values(data)
            write_values(SPREADSHEET_ID, 'Tabs!D2:D', values_to_write)
        except BaseException as err:
            print(f"Error {err=}, {type(err)=}")
            delete_files(COMPILATION_VIDEO_DIR)
            continue

    send_mail(count)


if __name__ == "__main__":
    main()
