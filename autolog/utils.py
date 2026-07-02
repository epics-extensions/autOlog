"""Autolog main functionnality"""

import logging
from autolog.cac import caget, is_connected


def check_multiple_condition(autolog_condition: dict):
    """
    Check several pv condition according to logical operator
    """
    logical_condition = autolog_condition["logical_condition"]
    several_condition = []
    for index, condition in enumerate(autolog_condition["pv"]):
        logging.debug(
            "  Checking condition %s of %s ...",
            {index + 1},
            {len(autolog_condition["pv"])},
        )
        pv_name = condition["condition_pv_name"]
        if not is_connected(pv_name):
            return False
        pv_value = condition["condition_pv_value"]
        logging.debug("   - Condition value: %s;", pv_value)
        condition = check_desired_pv_value(pv_name, pv_value)
        several_condition.append(condition)
    if len(autolog_condition["pv"]) == 1:
        if True in several_condition:
            logging.debug("Condition met, waiting to be triggered...")
            return True
        logging.debug("Condition not met")
        return False
    if logical_condition == "and":
        if all(several_condition):
            logging.debug(
                "The logical operator between condition is: %s", {logical_condition}
            )
            logging.debug("Condition met, waiting to be triggered...")
            return True
    if logical_condition == "or":
        if any(several_condition):
            logging.debug(
                "The logical operator between condition is: %s", {logical_condition}
            )
            logging.debug("Condition met, waiting to be triggered...")
            return True
    logging.debug("The logical operator between condition is: %s", {logical_condition})
    logging.debug("Condition not met")
    return False


def check_desired_pv_value(pv_name, pv_desired_value):
    """
    Check if actual PV value matches desired value using caget
    return:
    True: if actual PV value is in pv_desired_value
    False: if actual PV value is not in pv_desired_value
    """
    if not is_connected(pv_name):
        return False
    pv_actual_value = caget(pv_name)
    logging.debug("   - PV: %s;", {pv_name})
    logging.debug("   - Actual value: %s;", {pv_actual_value})
    if isinstance(pv_desired_value, int):
        if pv_actual_value == pv_desired_value:
            logging.debug("=> Result: True;")
            return True
    if isinstance(pv_desired_value, float):
        if pv_actual_value == pv_desired_value:
            logging.debug("=> Result: True;")
            return True
    elif isinstance(pv_desired_value, list) and all(
        isinstance(i, int) for i in pv_desired_value
    ):
        if pv_actual_value in pv_desired_value:
            logging.debug("=> Result: True;")
            return True
    logging.debug("=> Result: False;")
    return False


def define_trigger_action(autolog_trigger: dict):
    """
    Return True or False to indicate whether a log should be created.
    """
    pv_name = autolog_trigger["trigger_pv_name"]
    on_change = autolog_trigger["on_change"]

    if not is_connected(pv_name):
        return False

    pv_actual_value = caget(pv_name)

    if "pv_value" not in autolog_trigger:
        autolog_trigger.update({"pv_value": pv_actual_value})
        logging.debug(
            "Update PV Value in trigger dict: %s", autolog_trigger["pv_value"]
        )
        if on_change:
            logging.debug(
                "Acquisition of the first PV value, "
                "since log creation is triggered by a change in PV value..."
            )
            return False

    if "triggered" not in autolog_trigger:
        autolog_trigger.update({"triggered": False})

    old_value = autolog_trigger.get("pv_value")
    autolog_trigger.update({"pv_value": pv_actual_value})
    logging.debug("Update PV Value in trigger dict: %s", autolog_trigger["pv_value"])

    triggered = autolog_trigger.get("triggered")

    if check_desired_pv_value(pv_name, old_value):
        if triggered:
            logging.debug("Log already created once")
        else:
            logging.debug("Same value")
            logging.debug("Trigger condition not met")
        return False

    autolog_trigger.update({"triggered": False})

    if on_change:
        logging.debug("   - Trigger value: on change")
        logging.debug("Trigger condition met...")
        return True

    pv_value = autolog_trigger["trigger_pv_value"]
    logging.debug("   - Trigger value: %s;", pv_value)
    if check_desired_pv_value(pv_name, pv_value):
        logging.debug("Trigger condition met...")
        autolog_trigger.update({"triggered": True})
        return True
    logging.debug("Trigger condition not met")
    autolog_trigger.update({"triggered": False})
    return False
