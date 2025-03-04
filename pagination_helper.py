import requests
from urllib.parse import urlencode
from constants import MAX_PAGE_SIZE

def fetch_paginated_data(base_url, endpoint, headers, params, verbose=False):
    # Ensure the page_size is within allowable limits
    params['page_size'] = max(25, min(params.get('page_size', 100), MAX_PAGE_SIZE))
    
    all_data = []
    url = f"{base_url}{endpoint}?{urlencode(params)}"
    total_fetched_items = 0
    reported_item_count = None

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            body = response.json()
            if isinstance(body, dict) and 'data' in body:
                data = body['data']
            elif isinstance(body, list):
                data = body
            else:
                print("Unexpected response format.")
                print(body)
                break

            all_data.extend(data)
            total_fetched_items += len(data)

            if 'Item-Count' in response.headers:
                current_count = int(response.headers['Item-Count'])
                if reported_item_count is None:
                    reported_item_count = current_count
                    if verbose:
                        print(f"Reported total item count: {reported_item_count}")
                elif reported_item_count != current_count:
                    print("Error: Inconsistent item count reported across requests.")
                    break

            if verbose:
                print(f"Page fetched with {len(data)} items, running total: {total_fetched_items}")

            link_header = response.headers.get('Link')
            url = None
            if link_header:
                links = {part.split(";")[1].strip().replace('rel="', '').replace('"', ''): part.split(";")[0].strip('<>').strip()
                         for part in link_header.split(',')}
                url = links.get('next')
                if verbose and url:
                    print(f"Next page URL: {url}")
                elif verbose:
                    print("No next page found.")
        else:
            print(f"Failed to fetch data: {response.status_code}")
            break

    return all_data
