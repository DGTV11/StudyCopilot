Study Copilot
=============

## Requirements
- At least 8GB of RAM
- At least 11.5GB of free storage (just for the models)

## Installation
1) Install Python 3.12.0 (https://www.python.org/downloads/)
2) Install ollama (https://ollama.com/download)

3) Clone this repository

4) Cd into the StudyCopilot directory

5) (optional) Get an ngrok account and set up ngrok (https://dashboard.ngrok.com/get-started/setup/macos)

6) (optional) Get a free static domain and replace the text in server-url.txt with that domain

7) Install required Python libraries and backages
```sh
pip install -r requirements.txt
```

8) (optional) Enter your ngrok auth token using this command (replace `[AUTH TOKEN]` with your actual auth token)
```sh
ngrok config add-authtoken [AUTH TOKEN]
```

9) Pull the mistral, phi3, llava and nomic-embed-text models
```sh
ollama pull mistral
ollama pull phi3
ollama pull llava
ollama pull nomic-embed-text
```

10) Create a Hugging Face account (https://huggingface.co/)

11) Get gated model access for Mistral (model: mistralai/Mistral-7B-Instruct-v0.2)

12) Get a Hugging Face User Access Token (https://huggingface.co/settings/tokens)

13) Install the Hugging Face CLI
```sh
pip install -U "huggingface_hub[cli]"
```

14) Authenticate using your User Access Token
```sh
huggingface-cli login
```

15) (optional, needed for Autosurfer Online mode) Get a Google API key and a and a Programmable Search Engine ID (https://developers.google.com/custom-search/v1/overview)

## Usage
1) (optional) Start a tunnel
```sh
ngrok http 11434 --proto=http --host-header="localhost:11434" --domain=pleasing-precisely-sawfly.ngrok-free.app
```

2) Wait for the client to show something like
```sh
HTTP tunnel: https://xxxxxxxx.ngrok-free.app
```

3) Open another terminal, then run the client
```sh
python3 client/client.py
```

4) Wait for the client to show something like
```sh
Running on local URL:  http://127.0.0.1:7860

To create a public link, set `share=True` in `launch()`.
```

5) Open the local URL on your browser

## Features
1) Flashcard Generator
2) Autosurfer

## Notes
### ngrok
- You can only make 20000 HTTP/S requests per month and transfer 1 GB out of the server per month with a free account
- However, unless you are a heavy user of Study Copilot (in that case I applaud you), you are very unlikely to exhaust your free consumption limits

### AI
- Please double-check everything generated by AI; it may generate inaccurate information or information not found in the original input data!

## Credits
1) https://mattmazur.com/2023/12/14/running-mistral-7b-instruct-on-a-macbook/ for the suggestion of using Ollama
2) https://www.reddit.com/r/Anki/comments/11cgw1j/casting_a_spell_on_chatgpt_let_it_write_anki/ for system prompt of flashcards_helper
3) https://youtu.be/jENqvjpkwmw?si=n_nOXS_CLallmsfb and https://mer.vin/2024/02/ollama-embedding/ for the UI library suggestion and RAG idea
