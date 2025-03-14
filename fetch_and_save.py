import sys
import json
import os
import time
from datetime import datetime
from config_manager import load_config, CONFIG_PLACEHOLDERS
from token_manager import load_tokens, save_tokens
from fetcher import fetch_data
from oauth_manager import fetch_oauth2_token

def is_token_expired(tokens):
    """Check if the stored access token is expired."""
    if "expires_in" not in tokens or "access_token" not in tokens:
        return True  # Assume expired if missing expiration time

    expires_in = int(tokens["expires_in"])
    token_timestamp = tokens.get("timestamp", 0)  # Fallback to 0 if missing
    current_time = time.time()

    return current_time - token_timestamp >= expires_in

def get_valid_tokens(config, force=False):
    """Load and refresh OAuth tokens if needed."""
    if not force:
        tokens = load_tokens('creds/tokens.json')

    if not tokens or "access_token" not in tokens or is_token_expired(tokens) or force:
        print("Access token is missing or expired. Fetching new token...")
        tokens = fetch_oauth2_token(config)
        tokens["timestamp"] = time.time()  # Store timestamp of token issuance
        save_tokens('creds/tokens.json', tokens)

    return tokens

def get_cached_data(dir, name, verbose):
    cached_file = None
    latest_timestamp = 0
    now = time.time()

    for filename in os.listdir(dir):
        if filename.startswith(name+"_") and filename.endswith('.json'):
            filepath = os.path.join(dir, filename)
            file_timestamp = os.path.getmtime(filepath)

            if now - file_timestamp < 3600:  # Less than an hour old
                if file_timestamp > latest_timestamp:
                    latest_timestamp = file_timestamp
                    cached_file = filepath

    if cached_file:
        with open(cached_file, 'r') as f:
            cached_data = json.load(f)
            if verbose:
                print(f"Using cached data from {cached_file}")
            return cached_data
    else:
            return None


def fetch_and_save_data(version, entity_name, id=None, use_cache=True, verbose=True):
    """Fetches data from the specified endpoint and saves it to a timestamped JSON file.
    If a cached file is found and is less than an hour old, it is used instead of making a new API call.
    """

    if id:
        data_directory = 'data/'+entity_name
        id_str=str(id)
        endpoint="/"+version+"/"+entity_name+"/"+id_str
        page_size = None
        paginated = False
        fname_start=id_str
    else:
        data_directory = 'data'
        endpoint="/"+version+"/"+entity_name
        page_size = int(next((arg.split('=')[1] for arg in sys.argv if arg.startswith('--page_size=')), 250))
        paginated = True
        fname_start=entity_name

    os.makedirs(data_directory, exist_ok=True)
    if use_cache:
        cached_data = get_cached_data(data_directory, fname_start, verbose=verbose)
        if cached_data:
            return cached_data

    config = load_config('creds/config.json', CONFIG_PLACEHOLDERS)
    tokens = get_valid_tokens(config)

    data = fetch_data(config['base_url'], tokens['access_token'], endpoint, page_size=page_size, paginated=paginated, verbose=verbose)

    # Handle 401 (Unauthorized) error by refreshing token
    if isinstance(data, dict) and data.get("status") == 401:
        print("Received 401 Unauthorized. Refreshing token...")
        tokens = get_valid_tokens(config, force=True)  # Get fresh tokens

        # Retry fetching data with new token
        data = fetch_data(config['base_url'], tokens['access_token'], endpoint, page_size=page_size, paginated=paginated, verbose=verbose)

    if verbose:
        print(f"Total {entity_name} fetched: {len(data)}")

    # Save to a new timestamped file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    file_path = os.path.join(data_directory, f'{fname_start}_{timestamp}.json')
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
        print(f"{entity_name.capitalize()} saved to {file_path}")

    return data
