"""Unit tests for log_content.py using simulated PVs"""
import pytest
import json
from epics import caput, caget
from autolog.olog_api.log_content import define_body

@pytest.fixture
def mock_log_info():
    """Fixture providing mock log info"""
    return {
        "title": "Test Log",
        "description": "Test Description",
        "level": "INFO",
        "logbook": "test_logbook",
        "tags": ["tag1", "tag2"]  # Added tags
    }

@pytest.fixture
def mock_log_info_without_tags():
    """Fixture providing mock log info without tags"""
    return {
        "title": "Test Log",
        "description": "Test Description",
        "level": "INFO",
        "logbook": "test_logbook",
    }

@pytest.fixture
def mock_autolog_context():
    """Fixture providing mock autolog context with mmbi PV"""

    return [
        {
            "description": "Context 1",
            "pv": {
                "info_pv_name": "simple:intA",
                "info_pv_desc": True,
                "as_string": "yes"
            }
        },
        {
            "description": "Context 2",
            "pv": {
                "info_pv_name": "simple:floatA",
                "info_pv_desc": False,
                "as_string": "no"
            }
        }
    ]

@pytest.mark.log_content
def test_define_body_with_tags(simulated_pv, mock_log_info):
    """Test define_body with tags"""
    # Set up PV value
    caput("simple:intA", 42)  # Set a known value for the PV

    # Call the function
    body = define_body("testuser", "simple:intA", mock_log_info, {})

    # Verify the body
    log_entry = json.loads(body['logEntry'][1])
    assert log_entry["owner"] == "testuser"
    assert "Test Description" in log_entry["description"]
    assert log_entry["level"] == "INFO"
    assert log_entry["title"] == "Test Log"
    assert log_entry["logbooks"][0]["name"] == "test_logbook"
    assert "triggered by the PV: simple:intA" in log_entry["description"]
    assert "42" in log_entry["description"]

    # Verify tags
    assert len(log_entry["tags"]) == 2
    assert {"name": "tag1"} in log_entry["tags"]
    assert {"name": "tag2"} in log_entry["tags"]

@pytest.mark.log_content
def test_define_body_without_tags(simulated_pv, mock_log_info_without_tags):
    """Test define_body without tags"""
    # Set up PV value
    caput("simple:intA", 42)  # Set a known value for the PV

    # Call the function
    body = define_body("testuser", "simple:intA", mock_log_info_without_tags, {})

    # Verify the body
    log_entry = json.loads(body['logEntry'][1])
    assert log_entry["owner"] == "testuser"
    assert "Test Description" in log_entry["description"]
    assert log_entry["level"] == "INFO"
    assert log_entry["title"] == "Test Log"
    assert log_entry["logbooks"][0]["name"] == "test_logbook"
    assert "triggered by the PV: simple:intA" in log_entry["description"]
    assert "42" in log_entry["description"]

    # Verify tags are empty
    assert len(log_entry["tags"]) == 0

@pytest.mark.log_content
def test_define_body_with_several_context(simulated_pv, mock_log_info, mock_autolog_context):
    """Test create_context_desc without PV in context"""
    # Set up PV value
    caput("simple:intA", 42)  # Set a known value for the PV

    body = define_body("testuser", "simple:intA", mock_log_info, mock_autolog_context)

    # Verify the body
    log_entry = json.loads(body['logEntry'][1])
    assert "Context 1" in log_entry["description"]
    assert "Context 2" in log_entry["description"]
    assert "[PV_DESC]" in log_entry["description"]

    # Verify tags are included
    assert len(log_entry["tags"]) == 2
    assert {"name": "tag1"} in log_entry["tags"]
    assert {"name": "tag2"} in log_entry["tags"]