import os
import uuid
import requests
from urllib.parse import urlencode
from pagination_helper import fetch_paginated_data

def fetch_data(base_url, access_token, endpoint, page_size=100, updated_after=None, verbose=False, paginated=True):
    headers = {"Authorization": f"Bearer {access_token}"}
    nonce = uuid.uuid4().hex
    temp_dir = os.path.join('/tmp', nonce)
    os.makedirs(temp_dir, exist_ok=True)

    params = {'page_size': page_size}
    if updated_after:
        params['filter[updated_after]'] = updated_after

    # Fetch data using the pagination helper
    if paginated:
        data = fetch_paginated_data(base_url, endpoint, headers, params, verbose)
    else:
        url = f"{base_url}{endpoint}"
        if verbose:
            print("URL: "+url)
        response = requests.get(url, headers=headers)
        if verbose:
            print("Response: "+str(response.json()))
        if response.status_code == 200:
            data = response.json()
        else:
            print(f"Failed to fetch data: {response.status_code}")
            data = None

    return data
