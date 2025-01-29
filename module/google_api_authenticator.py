import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

REDIRECT_URI = os.environ['redirect_uri'] if 'redirect_uri' in os.environ else 'http://localhost:8501/callback'


def authenticate_and_save_credentials(client_secret_data, scopes, session_id):
    CLIENT_SECRET_DATA = client_secret_data
    SCOPES = scopes

    cred = None

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            print('client secret data is\n', CLIENT_SECRET_DATA)
            with open(f'dist/{session_id}_credentials.json', 'w') as f:
                match CLIENT_SECRET_DATA:
                    case dict():  # pass the class for type matching
                        content = json.dumps(CLIENT_SECRET_DATA, separators=(',', ':'))
                        f.write(content)
                    case str():
                        f.write(CLIENT_SECRET_DATA)
                    case _:
                        raise TypeError('Either string or dictionary is expected.')

            flow = InstalledAppFlow.from_client_secrets_file(
                f'dist/{session_id}_credentials.json', SCOPES)
            flow.redirect_uri = REDIRECT_URI

            return flow


def generate_token(client_secret_data, scopes, session_id='DIRECT_RUN'):
    CLIENT_SECRET_DATA = client_secret_data
    SCOPES = scopes
    service = authenticate_and_save_credentials(CLIENT_SECRET_DATA, SCOPES, session_id)

    return service


if __name__ == '__main__':
    generate_token(client_secret_data='credentials.json',
                   scopes=['https://www.googleapis.com/auth/drive.readonly'])
