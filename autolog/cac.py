"""
Channel Access Client (CAC) interaction functions through pyepics

More details about pyepics here: https://pyepics.github.io/pyepics/
"""

import logging
import epics


def is_connected(pv_name: str, timeout: int = 5, enable_log: bool = True) -> bool:
    """
    Check if a PV is connected by by its name.
    """
    if enable_log:
        logging.debug("CAC: checking if `%s` is connected...", {pv_name})
    try:
        pv = epics.pv.get_pv(pv_name)
        value = pv.get(as_numpy=False, use_monitor=False, timeout=timeout)
    except Exception as exc:
        if enable_log:
            logging.error("PV `%s` connection cannot be checked!", {pv_name})
        raise exc
    if value is None:
        if enable_log:
            logging.debug("PV `%s` is not connected.", {pv_name})
        return False
    if enable_log:
        logging.debug("PV `%s` is connected.", {pv_name})
    return True


def caget(pv_name: str, as_string: bool = False, enable_log: bool = True) -> object:
    """
    Get a PV by its name.
    """

    if enable_log:
        logging.debug("CAC: getting `%s`...", {pv_name})
    try:
        pv = epics.pv.get_pv(pv_name)
        value = pv.get(
            as_string=as_string,
            use_monitor=False,
        )
    except Exception as exc:
        if enable_log:
            logging.error("PV `%s` cannot be retrieved!", {pv_name})
        raise exc
    if enable_log:
        if len(str(value)) < 128:
            logging.debug("CAC: got `%s`:", {pv_name})
        else:
            logging.debug("CAC: got `%s` (value too long to be printed)", {pv_name})
    return value
