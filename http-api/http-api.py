import argparse

import io

import os

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def download_file(file_id: str, service=None):
    try:
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.getvalue()


def save_file(file: io.BytesIO, filename):
    try:
        with open(filename, 'wb') as f:
            f.write(file)
    except Exception as error:
        print(F'An error occurred: {error}')


def get_credentials():
    creds = None

    try:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json')
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('No valid credentials found.')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    except Exception as error:
        print(F'An error occurred: {error}')

    return creds


def get_id_by_name(service: None, filename: str) -> str:
    try:
        results = service.files().list(q=f"name='{filename}'").execute()
        files = results.get('files', [])

        if len(files) > 0:
            return files[0]['id']
        else:
            return None

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def main(filename):
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    id_by_name = get_id_by_name(service=service, filename=filename)
    save_file(download_file(file_id=id_by_name, service=service), filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Drive file downloader')
    parser.add_argument('filename', help='Name of the file to download')
    args = parser.parse_args()
    main(args.filename)
