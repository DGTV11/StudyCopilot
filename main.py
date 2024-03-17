import gradio as gr
import ollama

import modules.model_regen_helper as mrh
import modules.generate_flashcards as gen

fh_is_regenerating = False

def regen_flashcards_helper():
	global fh_is_regenerating
	
	fh_is_regenerating = True

	mrh.gen_model_from_modelfile('flashcards_helper', 
							  	__file__, 
							  	lambda: gr.Info('Creating flashcards_helper...'), 
							  	lambda: gr.Info('Finished!')
							  )
	
	fh_is_regenerating = False

if __name__ == '__main__':
	print('Checking if flashcards_helper model exists...')
	if 'flashcards_helper:latest' not in [model['name'] for model in ollama.list()['models']]:
		mrh.gen_model_from_modelfile('flashcards_helper', __file__, print('Creating flashcards_helper...'), print('Finished!'))	

	with gr.Blocks(theme=gr.themes.Default(primary_hue="red"), analytics_enabled=False, title="Study Copilot") as studyCopilot:
		gr.Markdown(
		"""
		# Study Copilot
		""")

		with gr.Tab('Flashcard Generator'):
			inp_cards_slides = gr.File(label="Slides:", file_count='multiple', file_types=['.pptx'])
			inp_cards_words = gr.Textbox(label="Notes:")

			with gr.Row():
				clear_inputs_btn = gr.ClearButton(components=[inp_cards_slides, inp_cards_words])
				generate_cards_btn = gr.Button(value="Generate Flashcards")
			
			stop = gr.Button(value="Stop", variant='primary')
			out_cards = gr.Markdown(label="A deck of flashcards:")
			clear_cards_btn = gr.ClearButton(components=[out_cards])
			regen_flashcards_helper_btn = gr.Button(value="Regenerate flashcards_helper", variant='secondary')
		with gr.Tab('Web Auto-Surfer'):
			pass

		regen_flashcards_helper_btn.click(fn=regen_flashcards_helper, inputs=[], outputs=[])
		gen_cards_event = generate_cards_btn.click(fn=gen.gen_flashcards, inputs=[inp_cards_slides, inp_cards_words], outputs=[out_cards])
		stop.click(fn=None, inputs=None, outputs=None, cancels=[gen_cards_event])

	print('Launching...')
	studyCopilot.launch()