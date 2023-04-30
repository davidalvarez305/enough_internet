from __future__ import print_function
import base64
from email.message import EmailMessage
import json

from constants import CREDENTIALS_DIR
from .auth import get_auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def send_mail(count):
    env_file = open(CREDENTIALS_DIR + "env.json")
    env = json.load(env_file)
    try:
        credentials = get_auth()
        service = build('gmail', 'v1', credentials=credentials)

        message = EmailMessage()

        message.set_content(f'''
        {count} videos were uploaded
        ''')

        message['To'] = str(env.get('EMAIL_TWO'))
        message['From'] = str(env.get('EMAIL_ONE'))
        message['Subject'] = f"{count} YouTube Videos Uploaded"

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }

        (service.users().messages().send
                        (userId="me", body=create_message).execute())

    except HttpError as error:
        print(F'An error occurred: {error}')