from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

# Access the token from the environment variable
access_token = os.getenv('CESIUM_ACCESS_TOKEN')

# Make a GET request to the Cesium API
url = 'https://api.cesium.com/v1/assets'
headers = {
    'Authorization': f'Bearer {access_token}'
}

# Send the request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    assets = response.json()
    print(assets)
else:
    print(f"Error: {response.status_code}")
    print(response.text)