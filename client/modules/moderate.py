import gradio as gr

from modules.host import HOST
import logging as log

def moderate(prompt: str) -> str:
    return HOST.chat(
        model="moderator",
        messages=[{"role": "user", "content": f"Text: {prompt}"}],
        stream=False,
    )["message"]["content"]


def check_moderation(module: str, response_str: str, raise_error_if_moderated: bool = True) -> None:
    if "not moderated" in response_str.lower():
        return None
    if raise_error_if_moderated:
        raise gr.Error(f"Content moderated! Reason: '{response_str}'")
    log.log_warning(f"Content moderated! Read at your own risk! Reason: '{response_str}'")
