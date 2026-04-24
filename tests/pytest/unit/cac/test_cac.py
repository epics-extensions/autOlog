"""test utils
simulated_pv: pvs simulated by tests/pytest/env/ioc.py
"""
import pytest
from epics import caput
from autolog.cac import is_connected, caget

@pytest.mark.cac
def test_is_connected(simulated_pv):
    value = is_connected("simple:notConnected")
    assert value is False

    value = is_connected('simple:intA')
    assert value is True

@pytest.mark.cac
def test_caget(simulated_pv):
    pv_name="simple:intA" 
    caput(pv_name, 4) 
    value = caget(pv_name)
    assert value is 4


    pv_name="simple:floatA"   
    caput(pv_name, 3.5) 
    value = caget(pv_name)
    assert value == 3.5

@pytest.mark.cac
def test_caget_as_string(simulated_pv):
    pv_name="simple:mbbiA"   
    value = caget(pv_name, False)
    assert isinstance(value, int)
    value = caget(pv_name, True)
    assert isinstance(value, str)