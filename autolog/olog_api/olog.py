"""Define the log to be sent to Olog"""
import uuid
import json
import logging
from autolog.cac import caget, is_connected

def define_body(username: str, trigger_pv_name: str, log_info: dict, autolog_context: dict):
    """
    Build API request body with log information
    """
    if autolog_context == {}:
        context_desc = ""
    else:
        context_desc = create_context_desc(trigger_pv_name, autolog_context)
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

    if 'attachment_file' in autolog_context :
        file_path = autolog_context['attachment_file']
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
    as_string = context_pv['as_string']
    more_info = ""
    if 'description' in autolog_context:
        autolog_desc = autolog_context['description']
        more_info = more_info + f"\n\n {autolog_desc} \n\n"
    if not context_pv.get("info_pv_name"):
        return more_info
    pv_name = context_pv['info_pv_name']
    if not is_connected(pv_name):
        more_info = more_info + "Not connected"
        return more_info
    info_pv_value = caget(pv_name)
    info_pv_value_as_string = caget(pv_name, as_string=True)
    if as_string == "yes":
        more_info = more_info +\
                    f"- {info_pv_value},\n\n" + \
                    f"- {info_pv_value_as_string}"
    elif as_string == "only":
        more_info = more_info +\
                    f"- {info_pv_value_as_string}"
    elif as_string == "no":
        more_info = more_info +\
                    f"- {info_pv_value}"
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
    try:
        body = {
            'logEntry': ('logEntry.json', f"{log_entry_json}", 'application/json'),
            'files': (f"{attachment_name}", open(file_path, 'rb'), "application/octet-stream")
            #todo: use "with":  Pylint R1732:consider-using-with
        }
        return body
    except FileNotFoundError as e:
        logging.error("Attachment file - File not found: `%s`!", {e})
        body = {
            'logEntry': ('logEntry', f"{log_entry_json}", 'application/json')
        }
        return body

def create_context_desc(trigger_pv_name: str, autolog_context: dict):
    """
    Create the description part of the log entry
    """
    more_info = "\n\n [Context] \n\n"
    for index, context in enumerate(autolog_context):
        if context.get('pv'):
            more_info = more_info + get_more_info(context)
        else:
            more_info = more_info + ""

    pv_actual_value = caget(trigger_pv_name)
    context_desc =\
        f"\n\nThe log creation has been triggered by the pv: {trigger_pv_name}, \
            with value: {pv_actual_value}" \
        + more_info \
        + "\n\n Log created automatically by the application AutOlog"

    return context_desc
