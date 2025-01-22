import os
from typing import Any

import pytest

from python_utils.env_vars import EnvVar


def mocked_caster():
    raise Exception


def setup_function():
    """setup any state tied to the execution of the given function.
    Invoked for every test function in the module.
    """
    for key, _ in os.environ.items():
        if key.startswith("TEST_"):
            del os.environ[key]


def test__get_env_var__is_found():
    os.environ["TEST_VAR"] = "my_value"
    env_var = EnvVar[str]("TEST_VAR", cast_fct=str).value

    assert env_var == "my_value"


def test__get_env_var__is_not_found():
    with pytest.raises(
        ValueError, match='Missing required environment variable "TEST_VAR"'
    ):
        EnvVar[str]("TEST_VAR", cast_fct=str)


def test__get_env_var__is_defaulted():
    env_var = EnvVar[str]("TEST_VAR", cast_fct=str, default="my_default_value").value

    assert env_var == "my_default_value"


def test__get_env_var__is_optional_aka_is_defaulted_to_none():
    env_var = EnvVar[str]("TEST_VAR", cast_fct=str, default=None).value  # pyright: ignore[reportGeneralTypeIssues]
    assert env_var is None


def test__get_env_var__is_defaulted_to_custom_cast_type():
    class MyType:
        def __init__(self, value: Any):
            self.value = value

    os.environ["TEST_VAR"] = "my_value"

    env_var = EnvVar[MyType]("TEST_VAR", cast_fct=MyType).value

    assert isinstance(env_var, MyType)
    assert env_var.value == "my_value"


def test_get_env_var__casting_failed():
    os.environ["TEST_VAR"] = "1,2,3"
    with pytest.raises(Exception, match="An error occurred when casting the value"):
        EnvVar[list[int]]("TEST_VAR", cast_fct=mocked_caster)  # pyright: ignore[reportGeneralTypeIssues]


def test__get_env_var__is_found_and_cast():
    os.environ["TEST_VAR"] = "123"
    env_var = EnvVar[int]("TEST_VAR", cast_fct=int).value

    assert env_var == 123
