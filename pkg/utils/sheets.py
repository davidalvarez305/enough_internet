from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .auth import get_auth


def convert_sheets_values(values):
    rows = []
    headers = values[0]

    for index, row in enumerate(values):
        obj = {}
        for idx, value in enumerate(row):
            obj[headers[idx]] = value
        if index > 0:
            obj['body'] = {
                "snippet": {
                    "title": "",
                    "description": ""
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
            rows.append(obj)
    return rows

def convert_to_write_values(data):
    rows = []
    for d in data:
        row = []
        for key, value in d.items():
            if 'count' in key:
                row.append(int(value) + 1)
        rows.append(row)
    return rows

def write_values(spreadsheet_id, range, values):
    try:
        credentials = get_auth()
        service = build('sheets', 'v4', credentials=credentials)

        sheet = service.spreadsheets()

        body = {
            "values": values
        }

        sheet.values().update(
            spreadsheetId=spreadsheet_id, range=range,
            valueInputOption="USER_ENTERED", body=body).execute()

    except HttpError as err:
        print(err)


def get_values(spreadsheet_id, range):
    try:
        credentials = get_auth()
        service = build('sheets', 'v4', credentials=credentials)

        sheet = service.spreadsheets()

        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=range).execute()

        values = result.get('values', [])

        if not values:
            return []

        return values
    except HttpError as err:
        print(err)
