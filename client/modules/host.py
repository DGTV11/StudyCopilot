from os import path

import ollama

with open(path.join(path.dirname(path.dirname(path.dirname(__file__))), 'server-url.txt'), 'r') as f:
    HOST_URL = 'https://' + f.read().strip()
    HOST = ollama.Client(HOST_URL)
