# SMTP Client

Author: Tikhonchik Nikolay (`okaykudes@gmail.com`)  

## About

The SMTP Client Python script is a tool that allows users to send emails using the Simple Mail Transfer Protocol (SMTP). It provides a simple and straightforward way to send emails programmatically from a Python script.

## Usage

To run the script, you need to do the following:  

- Locate the section of the script where the SMTP server settings are defined. You will typically find variables such as smtp_host, smtp_port, Modify these variables to match your SMTP server's configuration.

- Update the email-related variables in the config.json file. These variables include password, subject, sender_email, receiver_email,attachment folder and edit message in message.txt file. Modify them according to your requirements.
```bash
python smtp.py destination
```