"""Unit tests for requests.py"""
import pytest
import requests
from unittest.mock import patch, MagicMock
from autolog.olog_api.requests import post_request

@pytest.fixture
def mock_credentials():
    """Fixture providing mock credentials"""
    return {
        "api_url": "http://localhost:8080",
        "username": "testuser",
        "password": "testpass"
    }

@pytest.fixture
def mock_body():
    """Fixture providing mock request body"""
    return {
        "title": "Test Log",
        "description": "Test Description",
        "level": "INFO",
        "logbook": "test_logbook"
    }

@pytest.mark.requests
@patch('requests.put')
def test_post_request_success(mock_put, mock_credentials, mock_body):
    """Test successful post request"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_put.return_value = mock_response

    # Call the function
    post_request(mock_body, mock_credentials)

    # Verify the PUT request was called correctly
    mock_put.assert_called_once_with(
        "http://localhost:8080/logs/multipart",
        files=mock_body,
        auth=("testuser", "testpass"),
        timeout=10
    )

@pytest.mark.requests
@patch('requests.put')
def test_post_request_failure(mock_put, mock_credentials, mock_body):
    """Test failed post request"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_put.return_value = mock_response

    # Call the function
    post_request(mock_body, mock_credentials)

    # Verify the PUT request was called correctly
    mock_put.assert_called_once_with(
        "http://localhost:8080/logs/multipart",
        files=mock_body,
        auth=("testuser", "testpass"),
        timeout=10
    )

@pytest.mark.requests
@patch('requests.put')
def test_post_request_exception(mock_put, mock_credentials, mock_body):
    """Test post request when an exception occurs"""
    # Setup mock to raise an exception
    mock_put.side_effect = requests.exceptions.RequestException("Connection error")

    # Call the function
    post_request(mock_body, mock_credentials)

    # Verify the PUT request was called correctly
    mock_put.assert_called_once_with(
        "http://localhost:8080/logs/multipart",
        files=mock_body,
        auth=("testuser", "testpass"),
        timeout=10
    )