import ollama
import gradio as gr

def moderate(prompt: str) -> str:
    return ollama.chat(
        model='moderator',
        messages=[{'role': 'user', 'content': f'Text: {prompt}'}],
        stream=False,
    )['message']['content']

def check_moderation(response_str: str, raise_error_if_moderated: bool=True) -> None:
    if 'not moderated' in response_str.lower():
        return None
    if raise_error_if_moderated:
        raise gr.Error(f'Content moderated! Reason: \'{response_str}\'')
    gr.Warning(f'Content moderated! Read at your own risk! Reason: \'{response_str}\'')