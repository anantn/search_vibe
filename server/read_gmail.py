from __future__ import print_function
import base64
import logging

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


def decode_and_strip(encoded_messages: list[str]) -> list[str]:
    cleaned_messages = []
    for encoded_message in encoded_messages:
        # decode base64
        decoded_message = base64.urlsafe_b64decode(
            encoded_message.encode('ASCII'))

        # Parse HTML and return only the text
        soup = BeautifulSoup(decoded_message, 'html.parser')
        parsed_message = soup.get_text()

        # Remove extra spaces
        cleaned_message = ' '.join(parsed_message.split())

        cleaned_messages.append(cleaned_message)
    return cleaned_messages

# Extract the text content of the email.
def get_message_body(message: dict) -> str:
    # The email may have a direct message body.
    body = []
    if message['payload']['body'].get('data') is not None:
        body.append(message['payload']['body'].get('data'))
    # Or it may have a message body in parts.

    parts = []
    parts = message['payload'].get('parts')
    while parts is not None and len(parts) > 0:
        current_part = parts[0]
        if current_part['body'].get('data') is not None:
            body.append(current_part['body'].get('data'))
        parts.pop(0)
        if current_part.get('parts') is not None:
            parts.extend(current_part['parts'])

    return " ".join(decode_and_strip(body))


def extract_from(message: dict) -> str:
    for each in message['payload']['headers']:
        if each['name'] == 'From':
            return each['value']


def extract_subject(message: dict) -> str:
    for each in message['payload']['headers']:
        if each['name'] == 'Subject':
            return each['value']


def read_gmail_messages(creds: Credentials) -> list[dict]:
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', maxResults = 100).execute()
        messages = results.get('messages', [])

        if not messages:
            logging.log(logging.ERROR, 'No email messages found.')
            return
        logging.log(logging.INFO, f'Retrieved {len(messages)} email messages.')

        message_ids = get_message_ids(messages)

        formatted_messages = []
        for id in message_ids:
            message = service.users().messages().get(
                userId='me', id=id, format='full').execute()

            formatted_messages.append(
                {"From": extract_from(message),
                 "Subject": extract_subject(message),
                 "Body": get_message_body(message)})

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
