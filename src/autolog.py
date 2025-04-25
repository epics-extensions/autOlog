import requests
import epics
import time
import argparse
import uuid
import json
from connection import create_auth_object
from olog_data import read_data

def check_pv(pv):
    """
    Check the value of the pv to trigger the creation of a log
    """
    # The PV name that triggers the creation of a log
    pv_name = pv['trigger_pv_name']
    print(f"Name of the PV triggering the creation of a log: {pv_name}")

    # The PV value that triggers the creation of a log
    trigger_value = pv['trigger_pv_value']
    print(f"Trigger value: {trigger_value}")

    # The actual value of the PV
    get_pv = epics.caget(pv_name)
    print(f"Actual PV value: {get_pv}")

    # Test if actual PV value matches trigger PV value
    if get_pv == trigger_value:
        return True
    else:
        return False

def post_request(autolog, pv, token, api_url, username):
    """
    Create and send API request to Olog server
    """
    # Create description with default information and user information
    title = "[autOlog]: " + autolog['title']
    description = f"Log created automatically.\n\n Triggered by the pv: {pv['trigger_pv_name']}, with value: {pv['trigger_pv_value']} \n\n" + "Description:\n\n" +  autolog['description']
    body =  {
                   "owner": f"{username}",
                   "description": f"{description}",
                   "level": f"{autolog['level']}",
                   "title": f"{title}",
                   "logbooks": [
                       {
                           "name": f"{autolog['logbook']}"
                       }
                   ],
                   "attachments":[]
               }

    # Header with authentication token
    header = {
        "Authorization": f"Basic {token}",
    }
    # API url to create new logs
    log_url = api_url + "/logs/multipart"

    if autolog.get('attachment_file') is not None:
        file_path = autolog['attachment_file']
        attachment_id = str(uuid.uuid4())
        attachment_name = file_path.split('/')[-1]
        log_entry["attachments"].append({"id": f"{attachment_id}", "filename": f"{attachment_name}"})
        log_entry_json = json.dumps(log_entry)
        files = {
            'logEntry': ('logEntry.json', f"{log_entry_json}", 'application/json'),
            'files': (f"{attachment_name}", open(file_path, 'rb'), "application/octet-stream")
        }
    else:
        log_entry_json = json.dumps(log_entry)
        files = {
            'logEntry': ('logEntry', f"{log_entry_json}", 'application/json')
        }

    response = requests.put(log_url, files=files, headers=header)

    # Check if the request was successful
    if response.status_code == 200:
        print('Log entry created successfully.')
        print('Response:', response.json())
    else:
        print(f'Failed to create log entry. Status code: {response.status_code}')
        print('Response:', response.text)

def main() -> None:
    parser = argparse.ArgumentParser(description="A python tool to create automatically logs into Phoebus-Olog server, triggered by a PV value.")
    
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
    check_time = log['check_time']

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
                print("The pv has triggered the creation of a log once. Its value is still equal to the trigger value. Waiting...\n")
                time.sleep(check_time)
        else:
            print("Condition not met. Waiting...\n")
        
        # Wait for 5 seconds before next check
        time.sleep(check_time)

if __name__ == "__main__":
    main()

