"""test utils"""
import pytest
from epics import caput
from autolog.utils import check_desired_pv_value

@pytest.mark.unit
def test_check_desired_value_list(simulated_pv):
    """
    Test check_desired_value in autolog/utils
    """
    pv_name = 'simple:intA'
    caput(pv_name, 4)
    value = check_desired_pv_value(pv_name, [1, 2, 3, 4])
    assert value is True
    value = check_desired_pv_value(pv_name, [1, 2, 3])
    assert value is False

@pytest.mark.unit
def test_check_desired_value_int(simulated_pv):
    """
    Test check_desired_value in autolog/utils
    """
    pv_name = 'simple:intA'
    caput(pv_name, 4)
    value = check_desired_pv_value(pv_name, 4)
    assert value is True
    value = check_desired_pv_value(pv_name, 1)
    assert value is False

@pytest.mark.unit
def test_check_desired_value_float(simulated_pv):
    """
    Test check_desired_value in autolog/utils
    """
    pv_name = 'simple:floatA'
    caput(pv_name, 3.5)
    value = check_desired_pv_value(pv_name, 3.5)
    assert value is True
    value = check_desired_pv_value(pv_name, 1.2)
    assert value is False

@pytest.mark.unit
def test_check_desired_value_not_connected():
    """
    Test check_desired_value in autolog/utils
    """
    pv_name = 'simple:notConnected'
    value = check_desired_pv_value(pv_name, 1)
    assert value is False
