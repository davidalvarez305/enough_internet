import os

import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from .auth import get_auth

scopes = ["https://www.googleapis.com/auth/youtube.upload"]


def upload(path, body):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    credentials = get_auth()

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    request = youtube.videos().insert(
        part="snippet,status",
        notifySubscribers=True,
        body=body,
        media_body=MediaFileUpload(path)
    )
    response = request.execute()

    print(response)
