import gradio as gr
import requests

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain.text_splitter import CharacterTextSplitter

from modules.host import HOST, HOST_URL

def gen_queries(prompt: str) -> list[str]:
    gr.Info('Generating search queries...')
    queries_str = HOST.chat(
            model='search_query_generator',
            messages=[{'role': 'user', 'content': f'Prompt: {prompt}\n\nQueries:'}],
            stream=False,
    )['message']['content']

    splitted_queries = queries_str.split('\n')

    queries = []
    for splitted_query in splitted_queries:
        if splitted_query:
            query = splitted_query.strip()[1:-1]
            queries.append(query)

    return queries

def search(api_key: str, search_engine_id: str, queries: list[str]) -> list[Document]:
    search_docs = []
    for query in queries:
        gr.Info(f'Searching for \'{query}\'...')
        search_res = requests.get(
            'https://www.googleapis.com/customsearch/v1',
            params={
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
            },
        ).json()
    
        search_links = [item['link'] for item in search_res['items']][:5]
        loader = WebBaseLoader(search_links)
        search_docs.extend(loader.load())

    return search_docs

def make_vectorstore_retriever(search_docs: list[Document]) -> VectorStoreRetriever:
    gr.Info('Processing search results...')
    
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
    doc_splits = text_splitter.split_documents(search_docs)

    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=OllamaEmbeddings(model='nomic-embed-text', base_url=HOST_URL),
    )

    return vectorstore.as_retriever()
