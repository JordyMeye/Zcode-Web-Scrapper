"""
Starts a local HTTP server and opens the predictions dashboard in your browser.
Run: python serve.py
"""
import http.server
import webbrowser
import os
import threading

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def log_message(self, format, *args):
        pass  # silence request logs


def open_browser():
    webbrowser.open(f'http://localhost:{PORT}/dashboard.html')


if __name__ == '__main__':
    server = http.server.HTTPServer(('localhost', PORT), Handler)
    print(f'[+] Dashboard running at http://localhost:{PORT}/dashboard.html')
    print('[+] Press Ctrl+C to stop.\n')
    threading.Timer(0.8, open_browser).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[+] Server stopped.')
