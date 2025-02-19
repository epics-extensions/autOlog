import requests
import epics
import time
import argparse
from connection import create_auth_object
from olog_data import read_data

def check_pv(pv):
    """
    Check the value of the pv to trigger the creation of a log
    """
    # The PV name that triggers the creation of a log
    pv_name = pv['trigger_pv_name']
    print(f"Name of the pv which triggers the creation of a log: {pv_name}")

    # The PV value that triggers the creation of a log
    pv_value = pv['trigger_pv_value']
    print(f"Value of the pv to trigger the creation of a log: {pv_value}")

    # The actual value of the PV
    test = epics.caget(pv_name)
    print(f"The actual pv value: {test}")

    # Test if actual PV value matches trigger PV value
    if test == pv_value:
        return True
    else:
        return False

def post_request(autolog, pv, token, api_url, username):
    """
    Create and send API request to Olog server
    """
    # Create description with default information and user information
    title = "[autOlog]: " + autolog['title']
    description = f"Log created automatically.\n\n Triggered by the pv: {pv['trigger_pv_name']}, with value {pv['trigger_pv_value']} \n\n" + "Description:\n\n" + log['autolog']['description']
    body =  {
                   "owner": f"{username}",
                   "description": f"{description}",
                   "level": f"{autolog['level']}",
                   "title": f"{title}",
                   "logbooks": [
                       {
                           "name": f"{autolog['logbook']}"
                       }
                   ]
               }
    
    # Header with authentication token
    print(token)
    header = {
        "Authorization": f"Basic {token}",
        "content-type": "application/json",
    }

    # API url to create new logs
    log_url = api_url + "/logs"

    print(log_url)
    print(body)
    print(header)
    # Send API request to create new log
    response = requests.put(log_url, json=body, headers=header)
    print(response.json())

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description="A script to create automatically logs into Olog server")
    
    # Input toml file
    parser.add_argument("config", type=str,
    help="The configuration file with all the required data.")
    
    # Ask user for credentials
    parser.add_argument("-c", "--credentials", action='store_true',
    help="Ask user for username, password and api_url")
    
    args = parser.parse_args()

    # Extract values from configuration file
    log = read_data(args.config, args.credentials)
    autolog = log['autolog']
    pv = log['pv']
    api_url = log['api_url']
    username = log['username']
    password = log['password']

    # Get token
    token = create_auth_object(api_url, username, password)
    
    # Waiting loop
    while True:
        # If actual PV value matches trigger PV value
        create_log = check_pv(pv)
        if create_log:
            
            # Send API request to create new log
            post_request(autolog, pv, token, api_url, username)
            
            # Wait for the pv value to change
            while check_pv(pv):
                print("The pv triggered the creation of a log once. Its value is still equal to the trigger value. Waiting...\n")
                time.sleep(5)
        else:
            print("Condition not met. Waiting...\n")
        
        # Wait for 5 seconds before next check
        time.sleep(5)

