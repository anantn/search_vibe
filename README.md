# search_vibe
Use Cohere API to perform search over personal email data

# How to use this repo

This repo contains two projects that use Cohere's APIs.

## Similar document retrieval 

This project takes in a search query and returns a list of relevant documents from the document repository. The document repository is a list of 100 emails from your gmail.com mail service.

### How to run

From a terminal

> $python3 main_search_embeddings.py

This will open a browser window where you log in with your google.com credentials and allow access to this application to read your email. The script will download 100 email messages from your inbox and use that to generate embedding vectors and a search index.

The script will then run a search query over your email and print out the top search results.

## Question Answering on email messages

This project ... TBD
