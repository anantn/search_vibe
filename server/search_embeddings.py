import argparse
import logging
from typing import List
import search
import read_gmail
import pickle

class SearchEmbeddings:

    def __init__(self):
        # Get arguments from the command line
        parser = argparse.ArgumentParser()
        parser.add_argument('--save_emails', type=bool, required=False, default=True)
        parser.add_argument('--save_index', type=bool, required=False, default=True)
        parser.add_argument('--load_emails', type=bool, required=False, default=True)
        parser.add_argument('--load_index', type=bool, required=False, default=True)
        args = parser.parse_args()

        self.co = search.get_cohere_client()

        # Read emails from Gmail
        if args.load_emails:
            with open('emails.pickle', 'rb') as f:
                input = pickle.load(f)
        else:
            google_creds = read_gmail.get_google_credentials()
            input = read_gmail.read_gmail_messages(google_creds)
            
            if args.save_emails:
                with open('emails.pickle', 'wb') as f:
                    pickle.dump(input, f)

        self.input_strings = [f"{message['From']}\n{message['Subject']}\n{message['Body']}" for message in input]

        if args.load_index:
            self.search_index = search.load_index()
        else:
            # Generate embeddings for the data set
            embeddings = search.generate_embeddings(self.co, self.input_strings)

            # Create the search index
            self.search_index = search.create_index(embeddings)


    def search(self, query: str) -> List[str]:
        # Search for the query
        (result_indices, _) = search.search(query, self.search_index, self.co)

        logging.log(logging.INFO, f'''
            Found {len(result_indices)} results for {query}.''')
        return [self.input_strings[each] for each in result_indices]
