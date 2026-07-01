"""Unit tests for config.py"""

import pytest
import tempfile
import os
from autolog.config import read_data


@pytest.fixture
def valid_config():
    """Fixture providing a valid configuration"""
    config_content = """
    [credentials]
    username = "testuser"
    password = "testpass"
    api_url = "http://test.com/api"

    [main_log_info]
    title = "Test Log"
    description = "Test Description"
    level = "INFO"
    logbook = "test_logbook"
    check_time = 5
    tags = ["test"]
    attachment_files = ["test.txt"]

    [[autolog]]
    [[autolog.context]]
    description = "Test Context"

    [autolog.context.pv]
    info_pv_name = "test:pv1"
    info_pv_desc = true
    as_string = "yes"

    [autolog.trigger]
    trigger_pv_name = "test:trigger1"
    trigger_pv_value = [1, 2, 3]
    on_change = false

    [autolog.condition]
    logical_condition = "and"

    [[autolog.condition.pv]]
    condition_pv_name = "test:condition1"
    condition_pv_value = [1, 2, 3]
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(config_content)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def invalid_config():
    """Fixture providing an invalid configuration"""
    config_content = """
    [credentials]
    username = 123  # Invalid type
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(config_content)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.mark.config
def test_read_data_valid_config(valid_config, monkeypatch):
    """Test reading a valid configuration file"""
    # Mock input for credentials
    inputs = iter(["user", "pass", "http://api.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = read_data(valid_config, credentials_user_input=True)

    assert isinstance(result, dict)
    assert result["credentials"]["username"] == "user"
    assert result["credentials"]["password"] == "pass"
    assert result["credentials"]["api_url"] == "http://api.com"
    assert result["main_log_info"]["title"] == "Test Log"
    assert len(result["autolog"]) == 1


@pytest.mark.config
def test_read_data_invalid_config(invalid_config):
    """Test reading an invalid configuration file"""
    with pytest.raises(SystemExit):
        read_data(invalid_config, credentials_user_input=False)


@pytest.mark.config
def test_read_data_missing_trigger_values(valid_config):
    """Test configuration with missing trigger values"""
    # Modify the config to have both trigger_pv_value and on_change
    with open(valid_config, "a") as f:
        f.write(
            """
        [[autolog]]
        [autolog.trigger]
        trigger_pv_name = "test:trigger2"
        trigger_pv_value = [1, 2, 3]
        on_change = true
        """
        )

    with pytest.raises(SystemExit):
        read_data(valid_config, credentials_user_input=False)


@pytest.mark.config
def test_read_data_file_not_found():
    """Test reading a non-existent configuration file"""
    with pytest.raises(FileNotFoundError):
        read_data("nonexistent.toml", credentials_user_input=False)

