import requests
import base64

def create_auth_object(api_url, username, password):

    login_url = api_url + "/login"

    # Body request
    data = {
        'username': username,
        'password': password
    }

    # Send POST request to login
    response = requests.post(login_url, data)

    # Check if authentication succeded
    if response.status_code == 200:
        # Create token
        auth_string = f"{username}:{password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return encoded_auth
    else:
        print(f"Connection failed. Code : {response.status_code}")
        print(response)


    