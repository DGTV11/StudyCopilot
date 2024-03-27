import ollama

HOST = ollama.Client('https://pleasing-precisely-sawfly.ngrok-free.app')

def reload_host(host_url):
    global HOST
    HOST = ollama.Client(host_url)