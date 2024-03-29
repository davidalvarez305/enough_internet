import json
import os
import google_auth_oauthlib.flow
from oauth2client.client import OAuth2Credentials

from constants import CREDENTIALS_DIR

scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/cloud-platform"]


def get_token():
    env_file = open(CREDENTIALS_DIR + "env.json")
    env = json.load(env_file) 
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    client_secrets_file = str(env.get('SECRETS_FILE'))

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file, scopes)
    flow.redirect_uri = 'http://localhost:8000'

    authorization_url, _ = flow.authorization_url(prompt='consent')

    print("Click: ", authorization_url)

    code = input("Code:").strip()

    creds = flow.fetch_token(code=code)

    print(creds)

    credentials = OAuth2Credentials(
        access_token=flow.credentials.token,
        client_id=flow.credentials.client_id,
        client_secret=flow.credentials.client_secret,
        refresh_token=flow.credentials.refresh_token,
        token_expiry=flow.credentials.expiry,
        token_uri=flow.credentials.token_uri,
        user_agent=str(env.get('USER_AGENT')),
        id_token=flow.credentials.id_token,
        scopes=flow.credentials.scopes,
    )

    return credentials


get_token()
