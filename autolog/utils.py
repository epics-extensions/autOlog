"""Autolog main functionnality"""
import logging
from autolog.cac import caget, is_connected

def check_multiple_condition(autolog_condition: dict):
    """
    Check several pv condition according to logical operator
    """
    logical_condition = autolog_condition['logical_condition']
    several_condition = []
    for index, condition in enumerate(autolog_condition['pv']):
        logging.info("  Checking condition %s of %s", {index + 1}, {len(autolog_condition['pv'])})
        pv_name = condition['condition_pv_name']
        pv_value = condition['condition_pv_value']
        logging.info("   - Condition value: %s;", pv_value)
        condition = check_pv(pv_name, pv_value)
        several_condition.append(condition)
    if len(autolog_condition['pv']) == 1:
        if True in several_condition:
            logging.info("Condition met, waiting to be triggered...")
            return True
        logging.warning("Condition not met")
        return False
    if logical_condition == 'and':
        if all(several_condition):
            logging.info("The logical operator between condition is: %s", {logical_condition})
            logging.info("Condition met, waiting to be triggered...")
            return True
    if logical_condition == "or":
        if any(several_condition):
            logging.info("The logical operator between condition is: %s", {logical_condition})
            logging.info("Condition met, waiting to be triggered...")
            return True
    logging.info("The logical operator between condition is: %s", {logical_condition})
    logging.warning("Condition not met")
    return False

def check_pv(pv_name: str, pv_value: list[int]):
    """
    Check if actual PV value matches desired value
    """
    if not is_connected(pv_name):
        return False
    pv_actual_value = caget(pv_name)
    logging.info("   - PV: %s;", {pv_name})
    logging.info("   - Actual value: %s;", {pv_actual_value})
    if pv_actual_value in pv_value:
        logging.info("=> Result: True;")
        return True
    logging.info("=> Result: False;")
    return False

def trigger_action(autolog_trigger: dict):
    """
    Return True or False to indicate whether a log should be created.
    """
    pv_name = autolog_trigger['trigger_pv_name']
    on_change = autolog_trigger['on_change']
    if not autolog_trigger.get('pv_value'):
        pv_actual_value = caget(pv_name)
        autolog_trigger.update({'pv_value': pv_actual_value})
        logging.debug("Update PV Value in trigger dict: %s", autolog_trigger['pv_value'])
        if on_change:
            return False
    else:
        old_value = autolog_trigger.get('pv_value')
        pv_actual_value = caget(pv_name)
        logging.debug("Old PV value: %s", old_value)
        logging.debug("New PV value: %s", pv_actual_value)
        autolog_trigger.update({'pv_value': pv_actual_value})
        if pv_actual_value == old_value:
            logging.warning("Already created once")
            return False
        if on_change:
            logging.info("   - Trigger value: on change")
            return True
    pv_value = autolog_trigger['trigger_pv_value']
    logging.info("   - Trigger value: %s;", pv_value)
    trigger_log = check_pv(pv_name, pv_value)
    return trigger_log
