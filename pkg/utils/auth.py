import json
import requests
from oauth2client.client import OAuth2Credentials

from constants import CREDENTIALS_DIR

# This refreshes the auth token from Google's API.
def get_auth():
    env_file = open(CREDENTIALS_DIR + "env.json")
    env = json.load(env_file)
    f = open(CREDENTIALS_DIR + str(env.get('SECRETS_FILE')))
    data = json.load(f)

    client_id = data['web']['client_id']
    client_secret = data['web']['client_secret']
    token_uri = data['web']['token_uri']
    refresh_token = str(env.get('REFRESH_TOKEN'))

    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(token_uri, params=params)

    creds = response.json()

    credentials = OAuth2Credentials(
        access_token=creds['access_token'],
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        token_expiry=creds['expires_in'],
        token_uri=token_uri,
        user_agent=str(env.get('USER_AGENT')),
        scopes=creds['scope'],
    )

    return credentials
