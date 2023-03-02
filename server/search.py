import logging
import pickle
import cohere
import numpy as np
import re
import pandas as pd
from tqdm import tqdm
from datasets import load_dataset
import umap
import altair as alt
from sklearn.metrics.pairwise import cosine_similarity
from annoy import AnnoyIndex
import warnings
import read_gmail

INDEX_FILE_NAME = 'search_index.ann'
INDEX_PARAMS_FILE_NAME = 'search_index_params.pickle'

def get_cohere_client() -> cohere.Client:
    # Create a new Cohere client
    api_key = "7IhVaJPP1Nju2wtvPIvMF53cBWA5sNw5DNleTQKQ"
    return cohere.Client(api_key)

def generate_embeddings(co: cohere.Client, input: list[str]) -> np.array:
    # Generate embeddings for the input
    response = co.embed(
        model='large',
        texts=input,
        truncate='RIGHT')

    logging.log(logging.INFO, f'Generated embeddings for {len(input)} items.')
    return np.array(response.embeddings)

def create_index(embeddings: np.array) -> AnnoyIndex:
    # Create the search index, pass the size of embedding
    search_index = AnnoyIndex(embeddings.shape[1], 'angular')
    # Add all the vectors to the search index
    for i in range(len(embeddings)):
        search_index.add_item(i, embeddings[i])

    search_index.build(10) # 10 trees
    search_index.save(INDEX_FILE_NAME)

    # save index parameters in a pickle file
    with open(INDEX_PARAMS_FILE_NAME, 'wb') as f:
        pickle.dump([embeddings.shape[1], 'angular'], f)
    
    logging.log(logging.INFO, f'Created search index with {len(embeddings)} items.')
    return search_index

def load_index() -> AnnoyIndex:
    # load index parameters from a pickle file
    with open(INDEX_PARAMS_FILE_NAME, 'rb') as f:
        params = pickle.load(f)
    
        search_index = AnnoyIndex(params[0], params[1])
        search_index.load(INDEX_FILE_NAME)
        return search_index

def search(input: str, search_index: AnnoyIndex, co: cohere.Client) -> tuple[list[int], list[float]]:
    # Generate embeddings for the input
    response = co.embed(
        model='large',
        texts=[input],
        truncate='RIGHT')
    
    query_embed = response.embeddings
    
    # Retrieve the nearest neighbors
    similar_item_ids = search_index.get_nns_by_vector(query_embed[0],10,
                                                    include_distances=True)
    
    return similar_item_ids