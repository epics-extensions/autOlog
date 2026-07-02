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
        "tags": ["tag1", "tag2"],  # Added tags
        "attachment_files": ["test.txt"],
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
                "as_string": "yes",
            },
        },
        {
            "description": "Context 2",
            "pv": {
                "info_pv_name": "simple:floatA",
                "info_pv_desc": False,
                "as_string": "no",
            },
        },
    ]


@pytest.mark.log_content
def test_define_body(simulated_pv, mock_log_info):
    """Test define_body with tags"""
    caput("simple:intA", 42)

    log_entry, attachment_files = define_body(
        "testuser", "simple:intA", mock_log_info, {}
    )

    assert log_entry["owner"] == "testuser"
    assert "Test Description" in log_entry["description"]
    assert log_entry["level"] == "INFO"
    assert log_entry["title"] == "Test Log"
    assert log_entry["logbooks"][0]["name"] == "test_logbook"
    assert "triggered by the PV: simple:intA" in log_entry["description"]
    assert "42" in log_entry["description"]

    assert len(log_entry["tags"]) == 2
    assert {"name": "tag1"} in log_entry["tags"]
    assert {"name": "tag2"} in log_entry["tags"]

    assert "test.txt" in attachment_files[0]


@pytest.mark.log_content
def test_define_body_without_tags(simulated_pv, mock_log_info_without_tags):
    """Test define_body without tags"""

    caput("simple:intA", 42)

    log_entry, attachment_files = define_body(
        "testuser", "simple:intA", mock_log_info_without_tags, {}
    )

    assert log_entry["owner"] == "testuser"
    assert "Test Description" in log_entry["description"]
    assert log_entry["level"] == "INFO"
    assert log_entry["title"] == "Test Log"
    assert log_entry["logbooks"][0]["name"] == "test_logbook"
    assert "triggered by the PV: simple:intA" in log_entry["description"]
    assert "42" in log_entry["description"]

    assert len(log_entry["tags"]) == 0
    assert attachment_files == []


@pytest.mark.log_content
def test_define_body_with_several_context(
    simulated_pv, mock_log_info, mock_autolog_context
):
    """Test create_context_desc without PV in context"""
    caput("simple:intA", 42)

    log_entry, attachment_files = define_body(
        "testuser", "simple:intA", mock_log_info, mock_autolog_context
    )

    assert "Context 1" in log_entry["description"]
    assert "Context 2" in log_entry["description"]
    assert "[pv_context_desc]" in log_entry["description"]

    assert len(log_entry["tags"]) == 2
    assert {"name": "tag1"} in log_entry["tags"]
    assert {"name": "tag2"} in log_entry["tags"]
