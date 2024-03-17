import ollama
import gradio as gr

def moderate(prompt, raise_error_if_moderated=True) -> None:
    response = ollama.chat(
        model='moderator',
        messages=[{'role': 'user', 'content': f'Text: {prompt}'}],
        stream=False,
    )

    if 'not moderated' in response.lower():
        return None
    if raise_error_if_moderated:
        raise gr.Error(f'Content moderated! Reason: \'{response}\'')
    gr.Warning(f'Content moderated! Read at your own risk! Reason: \'{response}\'')