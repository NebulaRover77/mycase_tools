import json
import os
import sys

CONFIG_PLACEHOLDERS = {
    "client_id": "your_client_id",
    "domain": "your_domain",
    "auth_endpoint": "https://your_domain.com/oauth/authorize",
    "token_endpoint": "https://your_domain.com/oauth/token",
    "redirect_uri": "http://localhost:3000/callback",
    "local_endpoint": "https://your_domain.com/whatever/get-login-links",
    "base_url": "https://external-integrations.mycase.com",
    "response_type": "code",
    "scope": "openid"
}

def ensure_file(path, template):
    data_needs_update = False

    # Ensure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Create the file if it does not exist
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        with open(path, 'w') as file:
            json.dump(template, file, indent=4)
        print(f"Configuration file created at {path}.")
        print("Please fill in the required details and run the program again.")
        sys.exit(1)  # Exit the script

    # Load the existing data
    with open(path, 'r') as file:
        data = json.load(file)

    # Check if all keys are present
    for key, value in template.items():
        if key not in data:
            data[key] = value
            data_needs_update = True

    # If missing keys were added, update the file
    if data_needs_update:
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Updated {path} with missing keys. Please check and replace placeholders with actual values.")
        sys.exit(1)  # Exit the script

    # Ensure client_id is not a placeholder
    if data.get("client_id") == "your_client_id":
        print(f"Error: 'client_id' is still set to 'your_client_id' in {path}.")
        print("Please update the configuration file with the correct values and rerun the script.")
        sys.exit(1)  # Exit the script

def load_config(path, placeholders):
    ensure_file(path, placeholders)
    with open(path, 'r') as file:
        return json.load(file)
