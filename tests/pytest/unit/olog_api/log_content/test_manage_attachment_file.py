"""Unit tests for log_content.py using simulated PVs"""
from unittest.mock import patch
import pytest
import uuid
from autolog.olog_api.log_content import manage_attachment_file

@pytest.fixture
def mock_log_info():
    """Fixture providing mock log info"""
    return {
        "title": "Test Log",
        "description": "Test Description",
        "level": "INFO",
        "logbook": "test_logbook"
    }

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

@pytest.mark.log_content
def test_manage_attachment_file_success(simulated_pv, mock_log_info, tmp_path):
    """Test manage_attachment_file with successful file opening"""
    # Create a temporary file
    attachment_file = tmp_path / "test_attachment.txt"
    attachment_file.write_text("Test attachment content")

    # Call the function
    log_entry = {
        "owner": "testuser",
        "description": "Test Description",
        "level": "INFO",
        "title": "Test Log",
        "logbooks": [{"name": "test_logbook"}],
        "attachments": []
    }
    body = manage_attachment_file(log_entry, str(attachment_file))

    # Verify the body
    assert 'logEntry' in body
    assert 'files' in body

    # Verify the file information in the body
    files = body['files']
      # Ensure ('test_attachment.txt', <_io.BufferedReader name='/tmp/pytest-of-ac273043/pytest-31/test_manage_attachment_file_su0/test_attachment.txt'>, 'application/octet-stream')
    assert len(files) == 3

    # Verify the file details
    file_info = files[0]
    assert file_info == "test_attachment.txt"  # Verify the filename

    ## Verify the attachment is in the log entry
    #assert len(log_entry["attachments"]) == 3
    #assert log_entry["attachments"][0] == "test_attachment.txt"
    #assert log_entry["attachments"][1] == "Test attachment content"
    #assert log_entry["attachments"][2] == "application/octet-stream"

@pytest.mark.log_content
def test_manage_attachment_file_failure(simulated_pv, mock_log_info):
    """Test manage_attachment_file with file not found"""
    # Call the function with non-existent file
    log_entry = {
        "owner": "testuser",
        "description": "Test Description",
        "level": "INFO",
        "title": "Test Log",
        "logbooks": [{"name": "test_logbook"}],
        "attachments": []
    }

    # Patch the logging.error function
    with patch('logging.error') as mock_logging_error:
        body = manage_attachment_file(log_entry, "nonexistent.txt")

        # Verify the logging error was called with the correct message pattern
        mock_logging_error.assert_called_once()
        args, kwargs = mock_logging_error.call_args
        assert "Attachment file - File not found:" in args[0]
        assert "No such file or directory" in str(args[1])

    # Verify the body (should not include files)
    assert 'logEntry' in body
    assert 'files' not in body

    ## Verify the attachments list is empty
    #assert len(log_entry["attachments"]) == 1

@pytest.mark.log_content
def test_manage_attachment_file_with_context(simulated_pv, mock_log_info, tmp_path):
    """Test manage_attachment_file with context and attachment"""
    # Create a temporary file
    attachment_file = tmp_path / "test_attachment.txt"
    attachment_file.write_text("Test attachment content")

    # Create a context with attachment file
    mock_autolog_context = {
        "description": "Test Context",
        "pv": {
            "info_pv_name": "simple:intA",
            "info_pv_desc": True,
            "as_string": "yes"
        },
        "attachment_file": str(attachment_file)
    }

    # Call the function
    log_entry = {
        "owner": "testuser",
        "description": "Test Description",
        "level": "INFO",
        "title": "Test Log",
        "logbooks": [{"name": "test_logbook"}],
        "attachments": []
    }
    body = manage_attachment_file(log_entry, str(attachment_file))

    # Verify the body
    assert 'logEntry' in body
    assert 'files' in body
    assert body['files'][0] == "test_attachment.txt"

    # Verify the attachment is in the log entry
    assert len(log_entry["attachments"]) == 1
    assert log_entry["attachments"][0]["filename"] == "test_attachment.txt"