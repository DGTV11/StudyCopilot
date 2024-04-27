import gradio as gr


def log_info(module, text):
    gr.Info(text)
    print(f"{module} (INFO): {text}")


def log_warning(module, text):
    gr.Warning(text)
    print(f"{module} (WARNING): {text}")
