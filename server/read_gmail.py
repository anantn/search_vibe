from __future__ import print_function
import base64
import logging
import email
import re

import os.path
import sys
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_message_ids(messages: list[dict]) -> list[str]:
    return list(map(lambda x: x['id'], messages))


def body_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

def body_from_plain(plain: str) -> str:
    decoded = ""
    try:
        decoded = plain.decode("utf-8")
    except UnicodeDecodeError:
        decoded = plain.decode("latin-1")
    return decoded

# Extract plain text contents of the email.
def get_message_body(message: email.message.EmailMessage) -> str:
    body = ""
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition'))
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                body = body_from_plain(part.get_payload(decode=True))
            elif content_type == 'text/html' and 'attachment' not in content_disposition:
                body = body_from_html(part.get_payload(decode=True))
    else:
        content_type = message.get_content_type()
        if content_type == 'text/plain':
            body = body_from_plain(message.get_payload(decode=True))
        elif content_type == 'text/html':
            body = body_from_html(message.get_payload(decode=True))

    # Trim multiple newlines into a single newline.
    body = re.sub(r'[\r\n][\r\n]{2,}', '\n\n', body)
    return re.sub(r'[\n]{2,}', '\n', body)


def read_gmail_messages(creds: Credentials, maxResults: int = 100) -> list[dict]:
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=maxResults).execute()
        messages = results.get('messages', [])

        if not messages:
            logging.log(logging.ERROR, 'No email messages found.')
            return
        logging.log(logging.INFO, f'Retrieved {len(messages)} email messages.')

        message_ids = get_message_ids(messages)

        formatted_messages = []
        for id in message_ids:
            message = service.users().messages().get(
                userId='me', id=id, format='raw').execute()
            parsed = email.message_from_bytes(base64.urlsafe_b64decode(message['raw']), policy=email.policy.default)
            formatted_messages.append(
                {"Id": id,
                 "From": parsed['from'],
                 "Subject": parsed['subject'],
                 "Body": get_message_body(parsed)})

            logging.log(
                logging.INFO, f'Read and parsed message {id} from your email account.')

        return formatted_messages

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def get_google_credentials() -> Credentials:
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                sys.path[0] + '/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
