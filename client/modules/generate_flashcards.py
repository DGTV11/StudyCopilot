import os

import gradio as gr
from pptx import Presentation
from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer

import modules.logging as log
from modules.host import HOST


def send_to_model(flashcards_helper_model, text):
    stream = HOST.generate(
        model=f"flashcards_helper_{flashcards_helper_model}",
        prompt=f"\nText: {text}\n\nA deck of flashcards:\n",
        stream=True,
    )
    res_stream = ""

    log.log_info("Flashcard Generator", "Generating flashcards...")
    for chunk in stream:
        yield chunk["response"]

def gen_flashcards(
    flashcards_helper_model, slides_filepaths, image_filepaths, notes, get_slides_images
):
    match flashcards_helper_model:
        case "mistral":
            tokenizer = Tokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
            ctx_window = 32768 - 505
        case "phi3":
            tokenizer = Tokenizer.from_pretrained("microsoft/Phi-3-mini-4k-instruct")
            ctx_window = 4096 - 505
        case _:
            raise gr.Error(f"{flashcards_helper_model} is not a supported model.")

    num_token_func = lambda text: len(tokenizer.encode(text).ids)

    if (not slides_filepaths) and (not notes) and (not image_filepaths):
        raise gr.Error(
            "Please provide at least one slideshow and/or image file and/or text."
        )
    else:
        res_stream = ""
        if slides_filepaths:
            len_filepaths = len(slides_filepaths)
            for i, filepath in enumerate(slides_filepaths, start=1):
                slides_name = os.path.basename(filepath).split(".")[0] + "\n"
                slides = Presentation(filepath).slides
                len_slides = len(slides)
                log.log_info(
                    "Flashcard Generator",
                    f"Grabbing text from slideshow {i}/{len_filepaths} ({len(slides)} slides)...",
                )
                slides_notes = slides_name
                slides_notes_start_slide = 1
                for j, slide in enumerate(slides, start=1):
                    log.log_info(
                        "Flashcard Generator",
                        f"Reading slide {j}/{len_slides}...",
                        debug_only=True,
                    )
                    slide_notes = ""

                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            slide_notes += shape.text + "\n"
                        if get_slides_images and hasattr(shape, "image"):
                            log.log_info(
                                "Flashcard Generator",
                                f"Grabbing and describing image from slide {j}/{len_slides}...",
                            )
                            slide_notes += (
                                "\n"
                                + HOST.generate(
                                    model="llava",
                                    prompt="Describe the content of this image in detail as if it were text",
                                    images=[shape.image.blob],
                                )["response"]
                                + "\n"
                            )
                            log.log_info(
                                "Flashcard Generator", f"Finished describing image!"
                            )

                    slide_notes_num_tokens = num_token_func(slide_notes)
                    slides_notes_num_tokens = num_token_func(slides_notes)

                    if (
                        slides_notes_num_tokens + slide_notes_num_tokens > ctx_window
                    ):
                        log.log_info(
                            "Flashcard Generator",
                            f"Sending slides {slides_notes_start_slide}-{j-1} of slideshow {i}/{len_filepaths} to flashcards_helper_{flashcards_helper_model}...",
                        )
                        for res in send_to_model(flashcards_helper_model, slides_notes):
                            res_stream += res
                            yield res_stream + res
                        res_stream += "\n"
                        slides_notes = slides_name + slide_notes
                        slides_notes_start_slide = j
                    else:
                        slides_notes += slide_notes

                    if j == len_slides:
                        log.log_info(
                            "Flashcard Generator",
                            f"Sending slides {slides_notes_start_slide}-{j} of slideshow {i}/{len_filepaths} to flashcards_helper_{flashcards_helper_model}...",
                        )
                        for res in send_to_model(flashcards_helper_model, slides_notes):
                            res_stream += res
                            yield res_stream + res
                        res_stream += "\n"

        if image_filepaths:
            len_filepaths = len(image_filepaths)
            images_notes_start_image = 1
            images_notes = ""
            for i, filepath in enumerate(image_filepaths, start=1):
                image_notes = os.path.basename(filepath).split(".")[0] + "\n"

                log.log_info(
                    "Flashcard Generator",
                    f"Grabbing and describing image {i}/{len_filepaths}...",
                )
                image_notes = (
                    "\n"
                    + HOST.generate(
                        model="llava",
                        prompt="Describe the content of this image in detail as if it were text",
                        images=[filepath],
                    )["response"]
                    + "\n"
                )
                log.log_info("Flashcard Generator", f"Finished describing image!")

                image_notes_num_tokens = num_token_func(image_notes)
                images_notes_num_tokens = num_token_func(images_notes)

                if (
                    images_notes_num_tokens + image_notes_num_tokens > ctx_window
                ):
                    log.log_info(
                        "Flashcard Generator",
                        f"Sending images {images_notes_start_image}/{len_filepaths}-{i-1}/{len_filepaths} to flashcards_helper_{flashcards_helper_model}...",
                    )
                    for res in send_to_model(flashcards_helper_model, images_notes):
                        res_stream += res
                        yield res_stream + res
                    res_stream += "\n\n"
                    images_notes = image_notes
                    images_notes_start_image = i
                else:
                    images_notes += image_notes

                if i == len_filepaths:
                    log.log_info(
                        "Flashcard Generator",
                        f"Sending images {images_notes_start_image}/{len_filepaths}-{i}/{len_filepaths} to flashcards_helper_{flashcards_helper_model}...",
                    )
                    for res in send_to_model(flashcards_helper_model, images_notes):
                        res_stream += res
                        yield res_stream + res
                    res_stream += "\n\n"

        if notes.strip():
            splitter = TextSplitter.from_huggingface_tokenizer(tokenizer, ctx_window)

            chunks = splitter.chunks(notes)
            len_chunks = len(chunks)

            for i, chunk in enumerate(chunks, start=1):
                log.log_info(
                    "Flashcard Generator",
                    f"Sending chunk {i}/{len_chunks} of textual notes to flashcards_helper_{flashcards_helper_model}...",
                )
                for res in send_to_model(flashcards_helper_model, chunk):
                    res_stream += res
                    yield res_stream + res
                res_stream += "\n\n"
