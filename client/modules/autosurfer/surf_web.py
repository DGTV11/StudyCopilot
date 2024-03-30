import gradio as gradio
import requests

from modules.host import HOST

def gen_queries(prompt: str) -> list[str]:
    gr.Info('Sending files and text to search_query_generator...')
	queries_str = HOST.chat(
			model='search_query_generator',
			messages=[{'role': 'user', 'content': f'Prompt: {prompt}\n\nQueries:'}],
			stream=False,
	)['message']['content']

	gr.Info('Generating search queries...')

    splitted_queries = queries_str.split('\n')

    queries = []
    for splitted_query in splitted_queries:
        if splitted_query:
            query = splitted_query.strip()[1:-1]
            queries.append(query)

    return queries

def search():
    pass
