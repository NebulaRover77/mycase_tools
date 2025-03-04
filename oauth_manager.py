import requests
import sys
import webbrowser
import json
import secrets
from urllib.parse import urlparse, parse_qs, urlencode
from http.server import HTTPServer, SimpleHTTPRequestHandler

def open_authorization_url(config):
    state = secrets.token_urlsafe(16)  # Generates a random URL-safe text string, here 16 bytes long
    params = {
        "local_callback": "https://localhost:8000/callback",
        "client_id": config['client_id'],
        "redirect_uri": config['redirect_uri'],
        "scope": config['scope']
    }
    auth_url = f"{config['local_endpoint']}?{urlencode(params)}"
    webbrowser.open(auth_url)
    print("Please authorize access in the opened browser window.")

# Global dictionary to store token data
received_tokens = {}

class CallbackHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global received_tokens
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        if 'access_token' in query:
            received_tokens = {
                'access_token': query['access_token'][0],
                'token_type': query.get('token_type', [None])[0],
                'refresh_token': query.get('refresh_token', [None])[0],
                'expires_in': query.get('expires_in', [None])[0],
                'scope': query.get('scope', [None])[0],
                'firm_uuid': query.get('firm_uuid', [None])[0]
            }
            self.wfile.write("Token received successfully. You can close this window.".encode())
        else:
            self.wfile.write("Failed to receive token data.".encode())

def fetch_oauth2_token(config):
    open_authorization_url(config)
    # Create a simple server to listen for the callback
    server_address = ('', 8000)
    with HTTPServer(server_address, CallbackHandler) as httpd:
        httpd.handle_request()

    if received_tokens:
        return received_tokens
    else:
        print("Failed to obtain authorization code.")
        sys.exit(1)
