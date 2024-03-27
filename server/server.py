from os import path

from pyngrok import conf, ngrok

# ngrok http 11434 --host-header="localhost:11434" --domain=pleasing-precisely-sawfly.ngrok-free.app

with open(path.join(path.dirname(path.dirname(__file__)), 'server-url.txt'), 'r') as f:
    http_tunnel = ngrok.connect(addr=11434, proto='http', host_header="localhost:11434", domain=f.read())

conf.get_default().monitor_thread = False

ngrok_process = ngrok.get_ngrok_process()

print(f'HTTP tunnel: {http_tunnel.public_url}')

try:
    # Block until CTRL-C or some other terminating event
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print("Shutting down server.")

    ngrok.kill()
