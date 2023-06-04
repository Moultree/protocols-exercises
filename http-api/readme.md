# Google API Downloader

Author: Tikhonchik Nikolay (`okaykudes@gmail.com`)  

## About

The Google API Downloader is a Python script that allows you to download files from Google Drive using the Google Drive API. It provides a simple and convenient way to authenticate with Google, access files, and download them to your local machine.


## Installation

First, install the requrements:

```bash
pip install -r requirements.txt
```
Set up Google API credentials:

- Go to the Google Cloud Console.
- Create a new project or select an existing one.
- Enable the Google Drive API for the project.
- Create credentials (OAuth 2.0 client ID) for the project.
- Download the credentials file (JSON format).
- Rename the credentials file to credentials.json.
- Place the credentials.json file in the project directory.

## Usage

To run the script, you need to do the following:  

```bash
python http-api.py filename
```
The script will prompt you to authorize the application using your Google account. Follow the on-screen instructions to authorize the application and obtain the necessary credentials.