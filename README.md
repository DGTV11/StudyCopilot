# Study Copilot

## Requirements
- At least 8GB of RAM
- At least 5GB of free storage (just for the models)

## Installation
1) Install Python 3.12.0 (https://www.python.org)
2) Install ollama (https://ollama.com)

3) Cd into the StudyCopilot directory

4) Install required Python libraries and backages
```sh
pip install -r requirements.txt
```

5) Install the mistral and nomic-embed-text models
```sh
ollama pull mistral
ollama pull nomic-embed-text
```
Note: nomic-embed-text isn't being used yet so there is no need to pull it for now.

## Usage
1) Run the program
```sh
python3 main.py
```

2) Wait for it to show something like
```sh
Running on local URL:  http://127.0.0.1:7860

To create a public link, set `share=True` in `launch()`.
```

3) Open the local URL on your browser

## Features
1) Flashcard Generator
