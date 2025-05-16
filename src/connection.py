"""Module to manage Olog API request"""
import base64
import requests

def create_auth_object(api_url, username, password):
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
    response = requests.post(login_url, data, timeout=10)

    # Check if authentication succeded
    if response.status_code == 200:
        # Create token
        auth_string = f"{username}:{password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return encoded_auth

    print(f"Connection failed. Code : {response.status_code}")
    print(response)
    return None

def post_request(autolog, token, api_url):
    """
    Create and send API request to Olog server
    """

    # Header with authentication token
    header = {
        "Authorization": f"Basic {token}",
    }
    # API url to create new logs
    log_url = api_url + "/logs/multipart"
    response = requests.put(log_url, files=autolog, headers=header, timeout=10)

    # Check if the request was successful
    if response.status_code == 200:
        print('Log entry created successfully.')
        print('Response:', response.json())
    else:
        print(f'Failed to create log entry. Status code: {response.status_code}')
        print('Response:', response.text)
