import ollama
import gradio as gr

def moderate(prompt, raise_error_if_moderated=True) -> None:
    response = ollama.chat(
        model='moderator',
        messages=[{'role': 'user', 'content': f'Text: {prompt}'}],
        stream=False,
    )

    if 'not moderated' in response:
        return None
    if raise_error_if_moderated:
        raise gr.Error('Content moderated!')
    gr.Warning('Content moderated! Read at your own risk!')