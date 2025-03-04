import os
import uuid
import requests
from urllib.parse import urlencode
from pagination_helper import fetch_paginated_data

def fetch_data(base_url, access_token, endpoint, page_size=100, updated_after=None, verbose=False):
    headers = {"Authorization": f"Bearer {access_token}"}
    nonce = uuid.uuid4().hex
    temp_dir = os.path.join('/tmp', nonce)
    os.makedirs(temp_dir, exist_ok=True)

    params = {'page_size': page_size}
    if updated_after:
        params['filter[updated_after]'] = updated_after

    # Fetch data using the pagination helper
    data = fetch_paginated_data(base_url, endpoint, headers, params, verbose)
    return data
