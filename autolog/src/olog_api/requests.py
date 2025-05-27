"""Manage Olog API request"""
import base64
import logging
import sys
import requests

def create_auth_object(api_url: str, username:str, password:str):
    """
    Try to authenticate on Olog server and return a token
    """
    login_url = api_url + "/login"

    # Body request
    data = {
        'username': username,
        'password': password
    }

    # Send POST request to login
    try:
        response = requests.post(login_url, data, timeout=10)
        # Check if authentication succeded
        if response.status_code == 200:
            # Create token
            auth_string = f"{username}:{password}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            return encoded_auth
        logging.warning("Connection failed. Code : %s", {response.status_code})
        print(response)
        return None
    except requests.exceptions.MissingSchema as e:
        logging.warning("Invalid URL: %s", {e} )
        logging.warning("Check the provided credentials")
        sys.exit()

def post_request(body: dict, credentials: dict):
    """
    Create and send API request to Olog server
    """
    api_url = credentials['api_url']
    username = credentials['username']
    password = credentials['password']
    token = create_auth_object(api_url, username, password)
    # Header with authentication token
    header = {
        "Authorization": f"Basic {token}",
    }
    # API url to create new logs
    log_url = api_url + "/logs/multipart"
    response = requests.put(log_url, files=body, headers=header, timeout=10)

    # Check if the request was successful
    if response.status_code == 200:
        logging.info('Log entry created successfully.')
        logging.info('Response: %s', response.json())
    else:
        logging.warning("Failed to create log entry. Status code: %s", {response.status_code})
        logging.warning('Response: %s', response.text)
