Study Copilot
=============

## Requirements
- At least 8GB of RAM
- At least 4.4GB of free storage (just for the models)

## Installation
1) Install Python 3.12.0 (https://www.python.org/downloads/)
2) Install ollama (https://ollama.com/download)

3) Clone this repository

4) Cd into the StudyCopilot directory

5) Get an ngrok account and set up ngrok (https://dashboard.ngrok.com/get-started/setup/macos)

6) Get a free static domain and replace the text in server-url.txt with that domain

7) Install required Python libraries and backages
```sh
pip install -r requirements.txt
```

8) Enter your ngrok auth token using this command (replace `[AUTH TOKEN]` with your actual auth token)
```sh
ngrok config add-authtoken [AUTH TOKEN]
```

9) Pull the mistral and nomic-embed-text models
```sh
ollama pull mistral
ollama pull nomic-embed-text
```

## Usage
1) Start the server
```sh
python3 server/server.py
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
