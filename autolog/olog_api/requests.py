"""Manage Olog API request"""
import logging
import requests

def post_request(body: dict, credentials: dict):
    api_url = credentials['api_url']
    username = credentials['username']
    password = credentials['password']

    log_url = api_url + "/logs/multipart"

    try:
        response = requests.put(
            log_url,
            files=body,
            auth=(username, password),
            timeout=10
        )

        if response.status_code == 200:
            logging.info('Log entry created successfully.')
            logging.info('Response: %s', response.json())
        else:
            logging.error("Failed. Status code: %s", response.status_code)
            logging.error("Response: %s", response.text)

    except requests.exceptions.RequestException as e:
        logging.error("Request failed: %s", e)