import argparse
import logging
import search
import read_gmail
import pickle

if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(level=logging.INFO)

    # Get arguments from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_emails', type=bool, required=False, default=True)
    parser.add_argument('--save_index', type=bool, required=False, default=True)
    parser.add_argument('--load_emails', type=bool, required=False, default=False)
    parser.add_argument('--load_index', type=bool, required=False, default=False)
    parser.add_argument('--query', type=str, required=False, default="Do I have a github account?")
    args = parser.parse_args()

    co = search.get_cohere_client()

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

    input_strings = [f"{message['From']}\n{message['Subject']}\n{message['Body']}" for message in input]

    if args.load_index:
        search_index = search.load_index()
    else:
        # Generate embeddings for the data set
        embeddings = search.generate_embeddings(co, input_strings)

        # Create the search index
        search_index = search.create_index(embeddings)


    # Search for the query
    result = search.search(args.query, search_index, co)

    logging.log(logging.INFO, f'''
        Found {len(result[0])} results for {args.query}.''')

    logging.log(logging.INFO, f'''
        The results are: {[input[i]['Subject'] for i in result[0]]}
        ''')
