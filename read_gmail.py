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


def read_gmail() -> list[str]:
    creds = get_google_credentials()
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
            return
        logging.log(logging.INFO, f'Found {len(messages)} messages.')

        formatted_messages = []
        for each in messages:
            id = each['id']
            message = service.users().messages().get(
                userId='me', id=id, format='full').execute()
            if message['payload']['body']['size'] > 0:
                # decode base64
                encoded_message = message['payload']['body']['data']
                decoded_message = base64.urlsafe_b64decode(
                    encoded_message.encode('ASCII'))

                # Parse HTML and return only the text
                soup = BeautifulSoup(decoded_message, 'html.parser')
                body = soup.get_text()

                # Remove extra spaces
                body = ' '.join(body.split())
                formatted_messages.append(body)
                logging.log(logging.INFO, f'Added message {id} to formatted_messages.')

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
