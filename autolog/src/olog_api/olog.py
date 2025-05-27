"""Define the log to be sent to Olog"""
import uuid
import json
from cac import caget, is_connected

def define_body(username: str, context_desc: str, log_info: dict):
    """
    Build API request body with log information
    """
    main_desc = f"{log_info['description']}\n\n" + context_desc
    log_entry =  {
                   "owner": f"{username}",
                   "description": f"{main_desc}",
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

def get_more_info(autolog_context: dict):
    """
    Get more info with PV provided as key "info_pv_name" into TOML file. 
    """
    context_pv = autolog_context['pv']
    pv_name = context_pv['info_pv_name']
    as_string = context_pv['as_string']
    more_info = "\n\n [Context] \n\n"
    if autolog_context.get('description') is not None:
        autolog_desc = autolog_context.get('description')
        more_info = more_info + f"{autolog_desc} \n\n"
    if not is_connected(pv_name):
        more_info = more_info + "Not connected"
        return more_info
    info_pv_value = caget(pv_name)
    info_pv_value_as_string = caget(pv_name, as_string=True)
    if as_string == "yes":
        more_info = more_info +\
                    f"- [PV_VALUE] : {info_pv_value},\n\n" + \
                    f"- [PV_VALUE_AS_STRING] : {info_pv_value_as_string}"
    elif as_string == "only":
        more_info = more_info +\
                    f"- [PV_VALUE_AS_STRING] : {info_pv_value_as_string}"
    elif as_string == "no":
        more_info = more_info +\
                    f"- [PV_VALUE] : {info_pv_value}"
    more_info = more_info + f"\n\n - [PV_NAME] : {pv_name}"
    desc = context_pv['info_pv_desc']
    if desc:
        desc_pv = caget(f"{pv_name}.DESC")
        more_info = more_info + f"\n\n - [PV_DESC] : {desc_pv} \n\n"
    return more_info

def manage_attachment_file(log_entry: dict, file_path: str):
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

def create_context_desc(trigger_pv_name: str, autolog_context: dict):
    """
    Create the description part of the log entry
    """

    if autolog_context['pv'].get('info_pv_name') is not None:
        more_info = get_more_info(autolog_context)
    else:
        more_info = ""

    pv_actual_value = caget(trigger_pv_name)
    context_desc =\
        f"\n\nThe log creation has been triggered by the pv: {trigger_pv_name}, \
            with value: {pv_actual_value}" \
        + more_info \
        + "\n\n Log created automatically by the application AutOlog"

    return context_desc
