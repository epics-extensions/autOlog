"""Autolog main script"""
import time
import argparse
import uuid
import json
import epics
from connection import create_auth_object, post_request
from data import read_data

def define_action(pv):
    """
    Return True or False to indicate whether a log should be created.
    """
    if 'condition' in pv:
        pv_name = pv['condition']['condition_pv_name']
        pv_value = pv['condition']['condition_pv_value']
        condition = check_pv(pv_name, pv_value)
        if not condition:
            return False
    pv_name = pv['trigger_pv_name']
    pv_value = pv['trigger_pv_value']
    trigger_log = check_pv(pv_name, pv_value)
    return trigger_log

def check_pv(pv_name, pv_value):
    """
    Check if actual PV value matches desired value
    """
    pv_actual_value = epics.caget(pv_name)
    print(f"{pv_name}, actual value: {pv_actual_value}, list of desired one: {pv_value}")
    if pv_actual_value in pv_value:
        print("Match")
        return True
    print("No match \n")
    return False

def manage_attachment_file(log_entry, file_path):
    """
    Include attachment file into API request body
    """
    attachment_id = str(uuid.uuid4())
    attachment_name = file_path.split('/')[-1]
    log_entry["attachments"].append({"id": f"{attachment_id}", 
                                     "filename": f"{attachment_name}"})
    log_entry_json = json.dumps(log_entry)
    with open(file_path, 'rb') as file:
        body = {
            'logEntry': ('logEntry.json', f"{log_entry_json}", 'application/json'),
            'files': (f"{attachment_name}", file, "application/octet-stream")
        }
    return body

def define_autolog(username, log_info, pv):
    """
    Build API requestion body with log information
    """
    pv_name = pv['trigger_pv_name']
    pv_actual_value = epics.caget(pv_name)

    if pv['context'].get('info_pv_name') is not None:
        info_pv_name = pv['context']['info_pv_name']
        pv_info_value = epics.caget(info_pv_name, as_string=True)
        more_info = f"\n\n More information from {info_pv_name}: {pv_info_value}"
    else:
        more_info = ""

    description = log_info['description'] \
        + f"\n\nThe log creation has been triggered by the pv: {pv_name}, \
    with value: {pv_actual_value}" \
        + more_info \
        + "\n\n Log created automatically by the application AutOlog"

    log_entry =  {
                   "owner": f"{username}",
                   "description": f"{description}",
                   "level": f"{log_info['level']}",
                   "title": f"{log_info['title']}",
                   "logbooks": [
                       {
                           "name": f"{log_info['logbook']}"
                       }
                   ],
                   "attachments":[]
               }

    if log_info.get('attachment_file') is not None:
        file_path = log_info['attachment_file']
        body = manage_attachment_file(log_entry, file_path)
    else:
        log_entry_json = json.dumps(log_entry)
        body = {
            'logEntry': ('logEntry', f"{log_entry_json}", 'application/json')
        }
    return body

def create_log(credentials, log_info, pv):
    """
    Prepare API request content to create new log
    """
    api_url = credentials['api_url']
    username = credentials['username']
    password = credentials['password']

    token = create_auth_object(api_url, username, password)
    autolog_content = define_autolog(username, log_info, pv)
    post_request(autolog_content, token, api_url)

def main() -> None:
    """
    Main function
    """
    parser = argparse.ArgumentParser(description=
    "A python tool to create automatically logs into Phoebus-Olog server, triggered by a PV value.")
    parser.add_argument("config", type=str,
    help="The configuration file with all the required data.")

    parser.add_argument("-c", "--credentials", action='store_true',
    help="Ask user for username, password and api_url")

    args = parser.parse_args()

    config = read_data(args.config, args.credentials)
    log_info = config['autolog']
    pv = config['pv']
    credentials = config['credentials']
    check_time = config['pv']['check_time']
    create_once = False

    # Main thread
    while True:
        order = define_action(pv)
        if order:
            if not create_once:
                create_log(credentials, log_info, pv)
                create_once = True
            else:
                print("Already created once")
        else:
            create_once = False
        time.sleep(check_time)

if __name__ == "__main__":
    main()
