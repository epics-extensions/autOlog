import time
import subprocess
from pathlib import Path
import pytest

# Function to get the root directory of the Poetry project
def get_poetry_root():
    # Get the path to the pyproject.toml file
    pyproject_toml = Path(__file__).resolve().parents[1] / 'pyproject.toml'
    return pyproject_toml.parent


@pytest.fixture(scope="module")
def simulated_pv():
    """simulated_pv"""
    # Get the root directory of the Poetry project
    root_dir = get_poetry_root()
    # Get the absolute path to the script
    script_path = root_dir / 'tests/env/ioc.py'
    # Start the IOC process using a context manager
    with subprocess.Popen(['python', str(script_path)]) as process:
        time.sleep(1)  # Wait for the IOC to start
        yield process
        # The process will be terminated automatically when exiting the 'with' block
        # Stop the IOC process
        process.terminate()
        process.wait()