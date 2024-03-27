from os import path

import ollama

with open(path.join(path.dirname(path.dirname(path.dirname(__file__))), 'server-url.txt'), 'r') as f:
    HOST = ollama.Client('https://pleasing-precisely-sawfly.ngrok-free.app')
