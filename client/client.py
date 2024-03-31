import os

import gradio as gr

import modules.host as host_module
import modules.model_regen as mrh
import modules.generate_flashcards as gen
import modules.autosurfer.gen_response as autosurfer

if __name__ == "__main__":
    for file in os.listdir(os.path.join(os.path.dirname(__file__), "modelfiles")):
        print(f"Checking if the '{file}' model exists...")
        if file[0] in [".", "_"]:
            continue
        if f"{file}:latest" not in [
            model["name"] for model in host_module.HOST.list()["models"]
        ]:
            mrh.gen_model_from_modelfile(
                f"{file}",
                __file__,
                lambda: print(f"Creating the '{file}' model..."),
                lambda: print(f"'{file}' model created!"),
            )

    with gr.Blocks(
        theme=gr.themes.Default(primary_hue="red"),
        analytics_enabled=False,
        title="Study Copilot",
    ) as studyCopilot:
        gr.Markdown(
            """
		# Study Copilot
		"""
        )

        with gr.Tab("Flashcard Generator"):
            inp_cards_slides = gr.File(
                label="Slides:", file_count="multiple", file_types=[".pptx"]
            )
            inp_cards_words = gr.Textbox(label="Notes:")

            with gr.Row():
                clear_inputs_btn = gr.ClearButton(
                    components=[inp_cards_slides, inp_cards_words]
                )
                generate_cards_btn = gr.Button(value="Generate Flashcards")

            stop_flashcards_btn = gr.Button(value="Stop", variant="primary")
            out_cards = gr.Markdown(label="A deck of flashcards:")
            clear_cards_btn = gr.ClearButton(components=[out_cards])
        with gr.Tab("Web Auto-Surfer"):
            api_key = gr.Textbox(label="Google API Key:")
            search_engine_id = gr.Textbox(label="Search Engine ID:")

            autosurfer_chat = gr.Chatbot()
            prompt = gr.Textbox(label="Prompt:")

            moderate_checkbox = gr.Checkbox(label="Moderate", value=True)
            with gr.Row():
                stop_autosurfer_btn = gr.Button(value="Stop", variant="primary")
                clear_autosurfer_btn = gr.ClearButton(
                    components=[prompt, autosurfer_chat]
                )

        regen_flashcards_helper_btn = gr.Button(
            value="Regenerate models", variant="secondary"
        )

        regen_flashcards_helper_btn.click(
            fn=lambda: mrh.regen_models(__file__), inputs=[], outputs=[]
        )
        gen_cards_event = generate_cards_btn.click(
            fn=gen.gen_flashcards,
            inputs=[inp_cards_slides, inp_cards_words],
            outputs=[out_cards],
        )

        autosurf_event = prompt.submit(
            fn=autosurfer.gen_response,
            inputs=[
                api_key,
                search_engine_id,
                moderate_checkbox,
                prompt,
                autosurfer_chat,
            ],
            outputs=[prompt, autosurfer_chat],
        )

        stop_flashcards_btn.click(
            fn=None, inputs=None, outputs=None, cancels=[gen_cards_event]
        )
        stop_autosurfer_btn.click(
            fn=None, inputs=None, outputs=None, cancels=[autosurf_event]
        )

    print("Launching...")
    studyCopilot.launch()
