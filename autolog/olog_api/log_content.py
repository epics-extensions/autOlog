"""Define the log to be sent to Olog"""

import logging
from os.path import abspath
from autolog.cac import caget, is_connected


def define_body(
    username: str, trigger_pv_name: str, log_info: dict, autolog_context: dict
):
    """
    Build API request body with log information
    """
    context_desc = create_context_desc(trigger_pv_name, autolog_context)
    main_desc = f"{log_info['description']}\n\n" + context_desc

    log_entry = {
        "owner": f"{username}",
        "description": f"{main_desc}",
        "level": f"{log_info['level']}",
        "title": f"{log_info['title']}",
        "logbooks": [{"name": f"{log_info['logbook']}"}],
        "tags": [],
        "attachments": [],
    }

    tags_list = []

    if "tags" in log_info:
        for tag in log_info["tags"]:
            logging.debug("TAGS NAME: %s", {tag})
            tags_list.append({"name": tag})
        log_entry["tags"] = tags_list

    attachment_file_paths = []

    if "attachment_files" in log_info:
        for attachment_file in log_info["attachment_files"]:
            filename = abspath(attachment_file)
            attachment_file_paths.append(filename)

    return log_entry, attachment_file_paths


def get_more_info(context: dict):
    """
    Get more info with PV provided as key "info_pv_name" in TOML file.
    """
    more_info = "\n\n[Context]\n\n"

    if "description" in context:
        more_info += f"\n\n{context['description']}\n\n"

    if "pv" not in context or not context["pv"].get("info_pv_name"):
        return more_info

    context_pv = context["pv"]
    pv_name = str(context_pv["info_pv_name"])

    if not is_connected(pv_name):
        more_info += "Not connected"
        return more_info

    info_pv_value = caget(pv_name)

    as_string = context_pv["as_string"]
    more_info += f"\n- [pv_context_name] {pv_name} \n\n"
    if as_string == "yes":
        info_pv_value_as_string = caget(pv_name, as_string=True)
        more_info += f"- [pv_context_value] {info_pv_value} \n\n - [pv_context_value_as_string] {info_pv_value_as_string} \n\n"
    elif as_string == "only":
        info_pv_value_as_string = caget(pv_name, as_string=True)
        more_info += f"- [pv_context_value_as_string] {info_pv_value_as_string} \n\n"
    else:
        more_info += f"- [pv_context_value] {info_pv_value} \n\n"

    if context_pv.get("info_pv_desc", False):
        desc_pv = caget(f"{pv_name}.DESC")
        more_info += f"- [pv_context_desc]: {desc_pv}"
    return more_info


def create_context_desc(trigger_pv_name: str, autolog_context: dict):
    """
    Create the description part of the log entry
    """
    more_info = ""
    if autolog_context != {}:
        for index, context in enumerate(autolog_context):
            more_info = more_info + get_more_info(context)

    pv_actual_value = caget(trigger_pv_name)
    context_desc = (
        f"\n\nThe log creation has been triggered by the PV: {trigger_pv_name}, \
            with value: {pv_actual_value}"
        + more_info
        + "\n\n Log created automatically by the application AutOlog"
    )

    return context_desc
