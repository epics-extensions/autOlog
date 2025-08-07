"""test utils
simulated_pv: pvs simulated by tests/pytest/env/ioc.py
"""
import pytest
from epics import caput
from autolog.utils import define_trigger_action

@pytest.mark.utils
def test_define_trigger_action_on_change(simulated_pv):
    """
    Test check_desired_value in autolog/utils
    """
    autolog_trigger = {
        'trigger_pv_name': 'simple:intA', ## default value, not relevant when single condition
        'on_change': True,
    }
    pv_name = 'simple:intA'

    caput(pv_name, 1)
    value = define_trigger_action(autolog_trigger)
    assert value is False
    value = define_trigger_action(autolog_trigger)
    assert value is False

    caput(pv_name, 4)
    value = define_trigger_action(autolog_trigger)
    assert value is True

@pytest.mark.utils
def test_define_trigger_action_int(simulated_pv):
    """
    Test check_desired_value in autolog/utils
    """
    autolog_trigger = {
        'trigger_pv_name': 'simple:intA', ## default value, not relevant when single condition
        'trigger_pv_value': 3,
        'on_change': False # default value
    }
    pv_name = 'simple:intA'

    caput(pv_name, 4)
    value = define_trigger_action(autolog_trigger)
    assert value is False

    caput(pv_name, 3)
    value = define_trigger_action(autolog_trigger)
    assert value is True

@pytest.mark.utils
def test_define_trigger_action_list(simulated_pv):
    """
    Test check_desired_value in autolog/utils
    """
    autolog_trigger = {
        'trigger_pv_name': 'simple:intA', ## default value, not relevant when single condition
        'trigger_pv_value': [1,2,4,5],
        'on_change': False # default value
    }
    pv_name = 'simple:intA'

    caput(pv_name, 3)
    value = define_trigger_action(autolog_trigger)
    assert value is False

    caput(pv_name, 4)
    value = define_trigger_action(autolog_trigger)
    assert value is True

@pytest.mark.utils
def test_define_trigger_action_not_connected(simulated_pv):
    """
    Test check_desired_value in autolog/utils
    """
    autolog_trigger = {
        'trigger_pv_name': 'simple:notConnected', ## default value, not relevant when single condition
        'on_change': True,
    }

    value = define_trigger_action(autolog_trigger)
    assert value is False