from pyngrok import ngrok

# ngrok http 11434 --host-header="localhost:11434" --domain=pleasing-precisely-sawfly.ngrok-free.app
http_tunnel = ngrok.connect(addr=11434, proto='http', host_header="localhost:11434", domain="pleasing-precisely-sawfly.ngrok-free.app")

ngrok_process = ngrok.get_ngrok_process()

try:
    # Block until CTRL-C or some other terminating event
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print("Shutting down server.")

    ngrok.kill()