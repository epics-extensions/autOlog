"""Unit tests for autolog.py"""
import pytest
import time
from unittest.mock import patch, MagicMock
from autolog.autolog import argparser, start_loop, main

@pytest.fixture
def mock_args():
    """Fixture providing mock command line arguments"""
    return MagicMock(config="test_config.toml", credentials=False, verbosity=2)

@pytest.fixture
def mock_user_data_without_condition():
    """Fixture providing mock user data"""
    return {
        "credentials": {
            "username": "testuser",
            "password": "testpass",
            "api_url": "http://test.com/api"
        },
        "main_log_info": {
            "title": "Test Log",
            "description": "Test Description",
            "level": "INFO",
            "logbook": "test_logbook",
            "check_time": 1
        },
        "autolog": [
            {
                "trigger": {
                    "trigger_pv_name": "test:trigger1",
                    "trigger_pv_value": [1, 2, 3],
                    "on_change": False
                },
                "context": [
                    {
                        "description": "Test Context",
                        "pv": {
                            "info_pv_name": "test:pv1",
                            "info_pv_desc": True,
                            "as_string": "yes"
                        }
                    }
                ]
            }
        ]
    }

@pytest.fixture
def mock_user_data():
    """Fixture providing mock user data with condition"""
    return {
        "credentials": {
            "username": "testuser",
            "password": "testpass",
            "api_url": "http://test.com/api"
        },
        "main_log_info": {
            "title": "Test Log",
            "description": "Test Description",
            "level": "INFO",
            "logbook": "test_logbook",
            "check_time": 1
        },
        "autolog": [
            {
                "trigger": {
                    "trigger_pv_name": "test:trigger1",
                    "trigger_pv_value": [1, 2, 3],
                    "on_change": False
                },
                "condition": [
                    {
                        "logical_condition": "or",
                        "pv": {
                            "condition_pv_name": "test:pv1",
                            "condition_pv_value": [0],
                        }
                    }
                ],
                "context": [
                    {
                        "description": "Test Context",
                        "pv": {
                            "info_pv_name": "test:pv1",
                            "info_pv_desc": True,
                            "as_string": "yes"
                        }
                    }
                ]
            }
        ]
    }

@pytest.mark.autolog
def test_argparser():
    """Test the argument parser"""
    test_args = ["test_config.toml", "-v", "3"]
    with patch('sys.argv', ['autolog.py'] + test_args):
        args = argparser()
        assert args.config == "test_config.toml"
        assert args.verbosity == 3
        assert args.credentials is False

@pytest.mark.autolog
@patch('autolog.autolog.define_trigger_action')
@patch('autolog.autolog.check_multiple_condition')
@patch('autolog.autolog.define_body')
@patch('autolog.autolog.post_request')
def test_start_loop_single_iteration(mock_post_request, mock_define_body, mock_check_condition, mock_define_trigger, mock_user_data):
    """Test the start_loop function for a single iteration"""
    # Setup mocks
    mock_define_trigger.return_value = True
    mock_check_condition.return_value = True
    mock_define_body.return_value = {"test": "body"}
    mock_post_request.return_value = {"status": "success"}

    # Patch time.sleep to break the loop after one iteration
    with patch('time.sleep') as mock_sleep:
        # Use a side effect to break the loop after one iteration
        def sleep_side_effect(seconds):
            raise StopIteration()

        mock_sleep.side_effect = sleep_side_effect

        try:
            start_loop(mock_user_data)
        except StopIteration:
            pass  # Expected exception to break the loop

    # Verify calls
    mock_define_trigger.assert_called_once()
    mock_check_condition.assert_called_once()
    mock_define_body.assert_called_once()
    mock_post_request.assert_called_once()

@pytest.mark.autolog
@patch('autolog.autolog.argparser')
@patch('autolog.autolog.read_data')
@patch('autolog.autolog.start_loop')
def test_main(mock_start_loop, mock_read_data, mock_argparser, mock_args, mock_user_data):
    """Test the main function"""
    # Setup mocks
    mock_argparser.return_value = mock_args
    mock_read_data.return_value = mock_user_data

    # Run main
    with patch('logging.basicConfig'):
        main()

    # Verify calls
    mock_argparser.assert_called_once()
    mock_read_data.assert_called_once_with(mock_args.config, mock_args.credentials)
    mock_start_loop.assert_called_once_with(mock_user_data)

@pytest.mark.autolog
@patch('autolog.autolog.define_trigger_action')
@patch('autolog.autolog.check_multiple_condition')
def test_start_loop_with_condition(mock_check_condition, mock_define_trigger, mock_user_data):
    """Test start_loop with condition not met"""
    # Setup mocks
    mock_define_trigger.return_value = True
    mock_check_condition.return_value = False  # Condition not met

    # Patch time.sleep to break the loop after one iteration
    with patch('time.sleep') as mock_sleep:
        # Use a side effect to break the loop after one iteration
        def sleep_side_effect(seconds):
            raise StopIteration()

        mock_sleep.side_effect = sleep_side_effect

        try:
            start_loop(mock_user_data)
        except StopIteration:
            pass  # Expected exception to break the loop

    # Verify that define_trigger_action was not called when condition is not met
    mock_define_trigger.assert_not_called()

@pytest.mark.autolog
@patch('autolog.autolog.define_trigger_action')
@patch('autolog.autolog.check_multiple_condition')
@patch('autolog.autolog.define_body')
@patch('autolog.autolog.post_request')
def test_start_loop_without_context(mock_post_request, mock_define_body, mock_check_condition, mock_define_trigger, mock_user_data):
    """Test start_loop without context"""
    # Modify mock data to remove context
    mock_user_data['autolog'][0].pop('context')

    # Setup mocks
    mock_define_trigger.return_value = True
    mock_check_condition.return_value = True
    mock_define_body.return_value = {"test": "body"}
    mock_post_request.return_value = {"status": "success"}

    # Patch time.sleep to break the loop after one iteration
    with patch('time.sleep') as mock_sleep:
        # Use a side effect to break the loop after one iteration
        def sleep_side_effect(seconds):
            raise StopIteration()

        mock_sleep.side_effect = sleep_side_effect

        try:
            start_loop(mock_user_data)
        except StopIteration:
            pass  # Expected exception to break the loop

    # Verify calls
    mock_define_trigger.assert_called_once()
    mock_check_condition.assert_called_once()
    mock_define_body.assert_called_once_with(
        mock_user_data['credentials']['username'],
        mock_user_data['autolog'][0]['trigger']['trigger_pv_name'],
        mock_user_data['main_log_info'],
        {}  # Empty context
    )
    mock_post_request.assert_called_once()

@pytest.mark.autolog
@patch('autolog.autolog.define_trigger_action')
@patch('autolog.autolog.define_body')
@patch('autolog.autolog.post_request')
def test_start_loop_without_condition(mock_post_request, mock_define_body, mock_define_trigger, mock_user_data_without_condition):
    """Test start_loop without condition"""

    # Setup mocks
    mock_define_trigger.return_value = True
    mock_define_body.return_value = {"test": "body"}
    mock_post_request.return_value = {"status": "success"}

    # Patch time.sleep to break the loop after one iteration
    with patch('time.sleep') as mock_sleep:
        # Use a side effect to break the loop after one iteration
        def sleep_side_effect(seconds):
            raise StopIteration()

        mock_sleep.side_effect = sleep_side_effect

        try:
            start_loop(mock_user_data_without_condition)
        except StopIteration:
            pass  # Expected exception to break the loop

    # Verify calls
    mock_define_trigger.assert_called_once()
    mock_define_body.assert_called_once()
    mock_post_request.assert_called_once()