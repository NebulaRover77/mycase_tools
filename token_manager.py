import json
import os

def ensure_token_file(path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        with open(path, 'w') as file:
            json.dump({}, file, indent=4)
        print(f"Created {path} with initial empty structure.")

def load_tokens(path):
    ensure_token_file(path)
    with open(path, 'r') as file:
        return json.load(file)

def save_tokens(path, tokens):
    with open(path, 'w') as file:
        json.dump(tokens, file, indent=4)
