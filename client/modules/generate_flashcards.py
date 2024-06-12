import os
from time import time

import gradio as gr
from pptx import Presentation
from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer

import modules.logging as log
from modules.host import HOST
from modules.config import CONFIG


def show_markdown(text):
    return text if text.startswith("```") and text.endswith("```") else "```" + text

def send_to_model(flashcards_helper_model, ctx_window, text):
    stream = HOST.generate(
        model=f"flashcards_helper_{flashcards_helper_model}",
        prompt=f"\nText: {text}\n\nA deck of flashcards:\n",
        stream=True,
        options={"num_ctx": ctx_window},
    )
    res_stream = ""

    log.log_info("Flashcard Generator", "Generating flashcards...")
    for chunk in stream:
        yield chunk["response"]

def gen_flashcards(
    flashcards_helper_model, slides_filepaths, image_filepaths, notes, get_slides_images
):
    gen_start_time = time()
    match flashcards_helper_model:
        case "mistral":
            tokenizer = Tokenizer.from_pretrained(
                "mistralai/Mistral-7B-Instruct-v0.2",
                auth_token=CONFIG["huggingface_user_access_token"],
            )
            ctx_window = 16384 #usually 32768 but reduced to lower RAM usage
        case "phi3":
            tokenizer = Tokenizer.from_pretrained(
                "microsoft/Phi-3-mini-4k-instruct",
                auth_token=CONFIG["huggingface_user_access_token"],
            )
            ctx_window = 4096
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
                    f"Reading slideshow {i}/{len_filepaths} ({len(slides)} slides)",
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
                                f"Grabbing and describing image from slide {j}/{len_slides}",
                            )

                            start_time = time()
                            slide_notes += (
                                "\n"
                                + HOST.generate(
                                    model="llava-llama3",
                                    prompt="Describe the content of this image in detail as if it were text",
                                    images=[shape.image.blob],
                                )["response"]
                                + "\n"
                            )
                            end_time = time()

                            log.log_info(
                                "Flashcard Generator",
                                f"Finished describing image! ({round(end_time-start_time, 2)}s)",
                            )

                    slide_notes_num_tokens = num_token_func(slide_notes)
                    slides_notes_num_tokens = num_token_func(slides_notes)

                    if slides_notes_num_tokens + slide_notes_num_tokens > ctx_window:
                        log.log_info(
                            "Flashcard Generator",
                            f"Sending slides {slides_notes_start_slide}-{j-1} of slideshow {i}/{len_filepaths} to flashcards_helper_{flashcards_helper_model} ({slides_notes_num_tokens}/{ctx_window} tokens)",
                        )

                        start_time = time()
                        for res in send_to_model(flashcards_helper_model, ctx_window, slides_notes):
                            res_stream += res
                            yield res_stream
                        end_time = time()

                        log.log_info(
                            "Flashcard Generator",
                            f"Finished generating batch of flashcards ({round(end_time-start_time, 2)}s)",
                        )

                        res_stream += "\n\n"
                        slides_notes = slides_name + slide_notes
                        slides_notes_start_slide = j
                    else:
                        slides_notes += slide_notes

                    if j == len_slides:
                        log.log_info(
                            "Flashcard Generator",
                            f"Sending slides {slides_notes_start_slide}-{j} of slideshow {i}/{len_filepaths} to flashcards_helper_{flashcards_helper_model} ({slides_notes_num_tokens + slide_notes_num_tokens}/{ctx_window} tokens)",
                        )

                        start_time = time()
                        for res in send_to_model(flashcards_helper_model, ctx_window, slides_notes):
                            res_stream += res
                            yield res_stream
                        end_time = time()

                        log.log_info(
                            "Flashcard Generator",
                            f"Finished generating batch of flashcards ({round(end_time-start_time, 2)}s)",
                        )

                        res_stream += "\n\n"

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

                start_time = time()
                image_notes = (
                    "\n"
                    + HOST.generate(
                        model="llava-llama3",
                        prompt="Describe the content of this image in detail as if it were text",
                        images=[filepath],
                    )["response"]
                    + "\n"
                )
                end_time = time()

                log.log_info(
                    "Flashcard Generator",
                    f"Finished describing image! ({round(end_time-start_time, 2)}s)",
                )

                image_notes_num_tokens = num_token_func(image_notes)
                images_notes_num_tokens = num_token_func(images_notes)

                if images_notes_num_tokens + image_notes_num_tokens > ctx_window:
                    log.log_info(
                        "Flashcard Generator",
                        f"Sending images {images_notes_start_image}/{len_filepaths}-{i-1}/{len_filepaths} to flashcards_helper_{flashcards_helper_model} ({images_notes_num_tokens}/{ctx_window} tokens)",
                    )

                    start_time = time()
                    for res in send_to_model(flashcards_helper_model, ctx_window, images_notes):
                        res_stream += res
                        yield res_stream
                    end_time = time()

                    log.log_info(
                        "Flashcard Generator",
                        f"Finished generating batch of flashcards ({round(end_time-start_time, 2)}s)",
                    )

                    res_stream += "\n\n"
                    images_notes = image_notes
                    images_notes_start_image = i
                else:
                    images_notes += image_notes

                if i == len_filepaths:
                    log.log_info(
                        "Flashcard Generator",
                        f"Sending images {images_notes_start_image}/{len_filepaths}-{i}/{len_filepaths} to flashcards_helper_{flashcards_helper_model} ({images_notes_num_tokens + image_notes_num_tokens}/{ctx_window} tokens)",
                    )

                    start_time = time()
                    for res in send_to_model(flashcards_helper_model, ctx_window, images_notes):
                        res_stream += res
                        yield res_stream
                    end_time = time()

                    log.log_info(
                        "Flashcard Generator",
                        f"Finished generating batch of flashcards ({round(end_time-start_time, 2)}s)",
                    )

                    res_stream += "\n\n"

        if notes.strip():
            splitter = TextSplitter.from_huggingface_tokenizer(tokenizer, ctx_window)

            chunks = splitter.chunks(notes)
            len_chunks = len(chunks)

            for i, chunk in enumerate(chunks, start=1):
                chunk_num_tokens = num_token_func(chunk)
                log.log_info(
                    "Flashcard Generator",
                    f"Sending chunk {i}/{len_chunks} of textual notes to flashcards_helper_{flashcards_helper_model} ({chunk_num_tokens}/{ctx_window} tokens)",
                )

                start_time = time()
                for res in send_to_model(flashcards_helper_model, ctx_window, chunk):
                    res_stream += res
                    yield res_stream
                end_time = time()

                log.log_info(
                    "Flashcard Generator",
                    f"Finished generating batch of flashcards ({round(end_time-start_time, 2)}s)",
                )

                res_stream += "\n\n"

        gen_end_time = time()
        log.log_info(
            "Flashcard Generator",
            f"Finished generating flashcards ({round(gen_end_time-gen_start_time, 2)}s)",
        )
        yield res_stream
