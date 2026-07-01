"""Unit tests for requests.py"""

import pytest
import requests
from unittest.mock import MagicMock, patch

from autolog.olog_api.requests import post_request


@pytest.fixture
def mock_credentials():
    return {
        "api_url": "http://localhost:8080",
        "username": "testuser",
        "password": "testpass",
    }


@pytest.fixture
def mock_body():
    return {
        "title": "Test Log",
        "description": "Test Description",
        "level": "INFO",
        "logbook": "test_logbook",
        "attachments": [],
    }


@pytest.fixture
def mock_attachment_files(tmp_path):
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"

    file1.write_text("A")
    file2.write_text("B")

    return [file1, file2]


@pytest.mark.requests
@patch("requests.put")
def test_post_request_success(
    mock_put, mock_credentials, mock_body, mock_attachment_files
):
    mock_response = MagicMock(status_code=200)
    mock_response.json.return_value = {"status": "success"}
    mock_put.return_value = mock_response

    post_request(mock_body, mock_attachment_files, mock_credentials)

    mock_put.assert_called_once()

    _, kwargs = mock_put.call_args
    assert kwargs["auth"] == ("testuser", "testpass")
    assert kwargs["timeout"] == 10
    assert len(kwargs["files"]) == 3  # 2 files + logEntry


@pytest.mark.requests
@patch("requests.put")
def test_post_request_without_attachments(mock_put, mock_credentials, mock_body):
    mock_response = MagicMock(status_code=200)
    mock_put.return_value = mock_response

    post_request(mock_body, [], mock_credentials)

    mock_put.assert_called_once()

    _, kwargs = mock_put.call_args
    assert kwargs["auth"] == ("testuser", "testpass")
    assert kwargs["timeout"] == 10
    assert len(kwargs["files"]) == 1  # only logEntry


@pytest.mark.requests
@patch("requests.put")
def test_post_request_file_not_found(mock_put, mock_credentials, mock_body):
    post_request(mock_body, ["/tmp/does-not-exist"], mock_credentials)

    # File opening fails before the request is sent
    mock_put.assert_not_called()


@pytest.mark.requests
@patch("requests.put")
def test_post_request_bad_request(mock_put, mock_credentials, mock_body):
    mock_response = MagicMock(status_code=400)
    mock_response.text = "Bad Request"
    mock_put.return_value = mock_response

    post_request(mock_body, [], mock_credentials)

    mock_put.assert_called_once()


@pytest.mark.requests
@patch("requests.put")
def test_post_request_request_exception(mock_put, mock_credentials, mock_body):
    mock_put.side_effect = requests.exceptions.RequestException("Connection error")

    # Exception is handled inside post_request()
    post_request(mock_body, [], mock_credentials)

    mock_put.assert_called_once()
