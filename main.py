import gradio as gr
import ollama, os
from pptx import Presentation

print('Checking if flashcards_helper model exists...')
if 'flashcards_helper:latest' not in [model['name'] for model in ollama.list()['models']]:
	with open(os.path.join(os.path.dirname(__file__), 'Modelfile')) as file:
		print('Creating flashcards_helper from modelfile string...')
		ollama.create(model='flashcards_helper', modelfile=file.read())

def gen_flashcards(filepaths, notes):
	pptx_files_notes = ''
	if filepaths:
		len_filepaths = len(filepaths)
		for i, filepath in enumerate(filepaths, start=1):
			pptx_files_notes += os.path.basename(filepath).split('.')[0] + '\n'
			slides = Presentation(filepath).slides
			gr.Info(f'Grabbing text from slideshow {i}/{len_filepaths} ({len(slides)} slides)...')
			for slide in slides:
				for shape in slide.shapes:
					if hasattr(shape, 'text'):
						pptx_files_notes += shape.text + '\n'

	gr.Info('Reading slide texts and notes...')
	stream = ollama.chat(
			model='flashcards_helper',
			messages=[{'role': 'user', 'content': f'Text: {pptx_files_notes + notes}\n\nA deck of flashcards:'}],
			stream=True,
	)
	res_stream = ''

	gr.Info('Generating flashcards...')
	for chunk in stream:
		res_stream += chunk['message']['content']
		yield res_stream

with gr.Blocks(theme=gr.themes.Default(primary_hue="red")) as studyCopilot:
	gr.Markdown(
	"""
	# Study Copilot
	""")

	with gr.Tab('Flashcard Generator'):
		inp_cards_slides = gr.File(file_count='multiple', file_types=['.pptx'])	
		inp_cards_words = gr.Textbox(label="Notes:")

		with gr.Row():
			clear_inputs_btn = gr.ClearButton(components=[inp_cards_slides, inp_cards_words])
			generate_cards_btn = gr.Button(value="Generate Flashcards")
		
		stop = gr.Button(value="Stop", variant='primary')
		out_cards = gr.Markdown(label="A deck of flashcards:")
		clear_cards_btn = gr.ClearButton(components=[out_cards])
	with gr.Tab('Credits'):
		gr.Markdown(
		'''
		1) https://mattmazur.com/2023/12/14/running-mistral-7b-instruct-on-a-macbook/ for the suggestion of using Ollama
		2) https://www.reddit.com/r/Anki/comments/11cgw1j/casting_a_spell_on_chatgpt_let_it_write_anki/ for system prompt of flashcards_helper
		3) https://youtu.be/jENqvjpkwmw?si=n_nOXS_CLallmsfb and https://mer.vin/2024/02/ollama-embedding/ for the UI suggestion and RAG idea
		''')

	gen_cards_event = generate_cards_btn.click(fn=gen_flashcards, inputs=[inp_cards_slides, inp_cards_words], outputs=[out_cards])
	stop.click(fn=None, inputs=None, outputs=None, cancels=[gen_cards_event])

print('Launching...')
studyCopilot.launch()