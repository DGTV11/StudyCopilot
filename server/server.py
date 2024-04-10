from os import path

from pyngrok import conf, ngrok

conf.get_default().monitor_thread = False

with open(path.join(path.dirname(path.dirname(__file__)), 'server-url.txt'), 'r') as f:
    http_tunnel = ngrok.connect(addr=11434, bind_tls='false', proto='http', host_header="localhost:11434", domain=f.read().strip())

# ngrok http 11434 --bind-tls=false --proto=http --host-header="localhost:11434" --domain=pleasing-precisely-sawfly.ngrok-free.app
ngrok_process = ngrok.get_ngrok_process()

print(f'HTTP tunnel: {http_tunnel.public_url}')

try:
    # Block until CTRL-C or some other terminating event
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print('Shutting down HTTP tunnel.')
    ngrok.kill()
