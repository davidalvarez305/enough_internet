import os

import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
import auth

scopes = ["https://www.googleapis.com/auth/youtube.upload"]


def upload(path):
    print("Uploading Video...")
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    credentials = auth.get_auth()

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    request = youtube.videos().insert(
        part="snippet,status",
        notifySubscribers=True,
        body={
            "snippet": {
                "title": "TEST #1",
                "tags": ["comedy"],
                "description": "testing video",
            },
            "status": {
                "privacyStatus": "private"
            }
        },
        media_body=MediaFileUpload(path)
    )
    response = request.execute()

    print(response)
