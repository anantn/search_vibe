import logging
import search
import read_gmail

if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(level=logging.INFO)

    co = search.get_cohere_client()
    
    # Read emails from Gmail
    input = read_gmail.read_gmail()

    # Generate embeddings for the data set
    embeddings = search.generate_embeddings(co, input)

    # Create the search index
    search_index = search.create_index(embeddings)

    # Get the search query from the user
    query = "Is Akris on sale at Saks?"

    # Search for the query
    result = search.search(query, search_index, co)

    logging.log(logging.INFO, f'''
        Found {len(result[0])} results for {query}.
        The results are: {[input[i] for i in result[0]]}
        ''')