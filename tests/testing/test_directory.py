import os
import tempfile

import pytest

from python_utils.testing.directory import set_working_directory


def test__set_working_directory():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Get the current working directory before using the context manager
        original_cwd = os.getcwd()

        # Use the context manager to change the working directory
        with set_working_directory(temp_dir):
            # Check if the working directory has been changed, resolving symbolic links
            assert os.path.realpath(os.getcwd()) == os.path.realpath(temp_dir)

        # Check if the working directory has been restored to the original value, resolving symbolic links
        assert os.path.realpath(os.getcwd()) == os.path.realpath(original_cwd)


def test__set_working_directory__wrong_path():
    # Choose a non-existent directory for testing
    non_existent_path = "/path/that/does/not/exist"

    # Verify that the directory does not exist before the context
    assert not os.path.exists(non_existent_path)

    with pytest.raises(
        FileNotFoundError, match=f"No such file or directory: '{non_existent_path}'"
    ):
        with set_working_directory(non_existent_path):
            pass
