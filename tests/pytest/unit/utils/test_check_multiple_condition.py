"""test utils
simulated_pv: pvs simulated by tests/pytest/env/ioc.py
"""
import pytest
from epics import caput
from autolog.utils import check_multiple_condition

@pytest.mark.utils
def test_check_single_condition(simulated_pv):
    """
    Test check_desired_multiple_condition in autolog/utils
    """
    autolog_condition = {
        'logical_condition': 'and', ## default value, not relevant when single condition
        'pv': [
        {
            'condition_pv_name': 'simple:intA',
            'condition_pv_value': [2,5,4],
        }
        ]
    }
    caput("simple:intA", 1)
    value = check_multiple_condition(autolog_condition)
    assert value is False

    caput("simple:intA", 2)
    value = check_multiple_condition(autolog_condition)
    assert value is True

    autolog_condition = {
        'logical_condition': 'or', ## default value, not relevant when single condition
        'pv': [
        {
            'condition_pv_name': 'simple:intA',
            'condition_pv_value': [2,5,4],
        }
        ]
    }
    caput("simple:intA", 1)
    value = check_multiple_condition(autolog_condition)
    assert value is False

    caput("simple:intA", 2)
    value = check_multiple_condition(autolog_condition)
    assert value is True

@pytest.mark.utils
def test_check_multiple_condition_or(simulated_pv):
    """
    Test check_desired_multiple_condition in autolog/utils
    """
    autolog_condition = {
        'logical_condition': 'or',
        'pv': [{
            'condition_pv_name': 'simple:intA',
            'condition_pv_value': 3,
        }, 
        {
            'condition_pv_name': 'simple:intB',
            'condition_pv_value': [2,5,4],
        }
        ]
    }
    caput("simple:intA", 1)
    caput("simple:intB", 1)
    value = check_multiple_condition(autolog_condition)
    assert value is False

    caput("simple:intB", 2)
    value = check_multiple_condition(autolog_condition)
    assert value is True

    caput("simple:intA", 3)
    caput("simple:intB", 1)
    value = check_multiple_condition(autolog_condition)
    assert value is True

@pytest.mark.utils
def test_check_multiple_condition_and(simulated_pv):
    """
    Test check_desired_multiple_condition in autolog/utils
    """
    autolog_condition = {
        'logical_condition': 'and',
        'pv': [{
            'condition_pv_name': 'simple:intA',
            'condition_pv_value': 3,
        }, 
        {
            'condition_pv_name': 'simple:intB',
            'condition_pv_value': [2,5,4],
        }
        ]
    }
    caput("simple:intA", 1)
    caput("simple:intB", 1)
    value = check_multiple_condition(autolog_condition)
    assert value is False

    caput("simple:intA", 3)
    caput("simple:intB", 1)
    value = check_multiple_condition(autolog_condition)
    assert value is False

    caput("simple:intB", 2)
    value = check_multiple_condition(autolog_condition)
    assert value is True

@pytest.mark.utils
def test_check_multiple_condition_not_connected(simulated_pv):
    """
    Test check_desired_multiple_condition in autolog/utils
    """
    autolog_condition = {
        'logical_condition': 'and',
        'pv': [{
            'condition_pv_name': 'simple:notConnected',
            'condition_pv_value': 3,
        }, 
        {
            'condition_pv_name': 'simple:notConnected',
            'condition_pv_value': [2,5,4],
        }
        ]
    }

    value = check_multiple_condition(autolog_condition)
    assert value is False
