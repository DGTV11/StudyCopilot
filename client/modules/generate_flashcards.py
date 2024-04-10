import os

import gradio as gr
from pptx import Presentation

from modules.host import HOST

def gen_flashcards(slides_filepaths, image_filepaths, notes):
    if (not slides_filepaths) and (not notes) and (not image_filepaths):
        raise gr.Error("Please provide at least one slideshow and/or image file and/or text.")
    else:
        slides_notes = ""
        if slides_filepaths:
            len_filepaths = len(slides_filepaths)
            for i, filepath in enumerate(slides_filepaths, start=1):
                slides_notes += os.path.basename(filepath).split(".")[0] + "\n"
                slides = Presentation(filepath).slides
                len_slides = len(slides)
                gr.Info(
                    f"Grabbing text from slideshow {i}/{len_filepaths} ({len(slides)} slides)..."
                )
                for j, slide in enumerate(slides, start=1):
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            slides_notes += shape.text + "\n"
                        if hasattr(shape, "image"):
                            gr.Info(f'Grabbing and describing image from slide {j}/{len_slides}...')
                            slides_notes += '\n' + HOST.generate(model="llava", prompt="Describe the content of this image in detail as if it were text", images=[shape.image.blob])['response'] + '\n'
                            gr.Info(f"Finished describing image!")

        images_notes = ""
        if image_filepaths:
            len_filepaths = len(image_filepaths)
            for i, filepath in enumerate(image_filepaths, start=1):
                gr.Info(f"Grabbing and describing image {i}/{len_filepaths}...")
                images_notes += '\n' + HOST.generate(model="llava", prompt="Describe the content of this image in detail as if it were text", images=[filepath])['response'] + '\n'
                gr.Info(f"Finished describing image!")

        gr.Info("Sending files and text to flashcards_helper...")
        stream = HOST.generate(
            model="flashcards_helper",
            prompt=f"\nText: {slides_notes + images_notes + notes}\n\nA deck of flashcards:\n",
            stream=True,
        )
        res_stream = ""

        gr.Info("Generating flashcards...")
        for chunk in stream:
            res_stream += chunk["response"]
            yield res_stream
