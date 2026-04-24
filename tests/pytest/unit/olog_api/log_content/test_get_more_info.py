"""Unit tests for log_content.py using simulated PVs"""
import pytest
from epics import caput, caget
from autolog.olog_api.log_content import get_more_info

@pytest.fixture
def mock_autolog_context():
    """Fixture providing mock autolog context"""
    return {
        "description": "Test Context",
        "pv": {
            "info_pv_name": "simple:intA",  # Use simulated PV
            "info_pv_desc": True,
            "as_string": "yes"
        }
    }

@pytest.fixture
def mock_autolog_context_no_pv_name():
    """Fixture providing mock autolog context without PV"""
    return {
        "description": "Test Context without PV",
        "pv": {
            "info_pv_desc": True,
            "as_string": "yes"
        }
    }

@pytest.fixture
def mock_autolog_context_no_desc():
    """Fixture providing mock autolog context without description"""
    return {
        "pv": {
            "info_pv_name": "simple:intB",  # Use another simulated PV
            "info_pv_desc": False,
            "as_string": "no"
        }
    }


@pytest.fixture
def mock_autolog_context_with_enum():
    """Fixture providing mock autolog context without description"""
    return {
        "description": "Enum Context",
        "pv": {
            "info_pv_name": "simple:mbbiA",  # Use simulated enum PV
            "info_pv_desc": True,
            "as_string": "yes"
        }
    }

@pytest.mark.log_content
def test_get_more_info_with_pv(simulated_pv, mock_autolog_context):
    """Test get_more_info with PV using simulated PV"""
    # Set up PV value
    caput("simple:intA", 42)  # Set a known value for the PV

    # Call the function
    more_info = get_more_info(mock_autolog_context)

    # Verify the more_info
    assert "Test Context" in more_info
    assert "simple:intA" in more_info
    assert "42" in more_info  # Verify the PV value is in the context
    assert "pv_context_name" in more_info
    assert "pv_context_desc" in more_info  # Verify the PV description is included

@pytest.mark.log_content
def test_get_more_info_without_pv(simulated_pv, mock_autolog_context_no_pv_name):
    """Test get_more_info without PV"""
    # Call the function
    more_info = get_more_info(mock_autolog_context_no_pv_name)

    # Verify the more_info
    assert "Test Context without PV" in more_info
    assert "Not connected" not in more_info  # Since there's no PV name

@pytest.mark.log_content
def test_get_more_info_without_desc(simulated_pv, mock_autolog_context_no_desc):
    """Test get_more_info without description"""
    # Set up PV value
    caput("simple:intB", 24)  # Set a known value for the PV

    # Call the function
    more_info = get_more_info(mock_autolog_context_no_desc)

    # Verify the more_info
    assert "24" in more_info  # Verify the PV value is in the context
    assert "pv_context_desc" not in more_info  # Since info_pv_desc is False

@pytest.mark.log_content
def test_get_more_info_with_float_pv(simulated_pv):
    """Test get_more_info with float PV"""
    # Create a context with float PV
    float_context = {
        "description": "Float Context",
        "pv": {
            "info_pv_name": "simple:floatA",  # Use simulated float PV
            "info_pv_desc": True,
            "as_string": "yes"
        }
    }

    # Set up PV value
    caput("simple:floatA", 3.14)  # Set a known value for the PV

    # Call the function
    more_info = get_more_info(float_context)

    # Verify the more_info
    assert "Float Context" in more_info
    assert "3.14" in more_info  # Verify the PV value is in the context
    assert "pv_context_desc" in more_info  # Verify the PV description is included

@pytest.mark.log_content
def test_get_more_info_with_enum_pv(simulated_pv, mock_autolog_context_with_enum):
    """Test get_more_info with enum PV"""

    # Call the function
    more_info = get_more_info(mock_autolog_context_with_enum)

    # Verify the more_info
    assert "Enum Context" in more_info
    assert "pv_context_desc" in more_info  # Verify the PV description is included
    assert "zero" in more_info #field ZRST mbbiA simulated pv

    # Verify the enum value is in the context (could be "zero", "one", etc.)
    assert any(enum_val in more_info for enum_val in ["zero", "one", "two"])