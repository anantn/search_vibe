import logging
import read_gmail

if __name__ == "__main__":
    # set up logging
    logging.basicConfig(level=logging.INFO)
    
    google_creds = read_gmail.get_google_credentials()
    messages = read_gmail.read_gmail_messages(google_creds)

    with open('gmail_messages.txt', 'w') as f:
        for message in messages:
            f.write(f"From: {message['From']}\nSubject: {message['Subject']}\nBody: {message['Body']}\n --SEPARATOR--\n")