import pytest
from logging import Logger
from typing import Any
from unittest.mock import Mock

from python_utils.loggers import log_and_raise


def test_simple_try_except():
    logger: Any = Mock(spec=Logger)

    original_exception = ValueError("original exception")

    with pytest.raises(original_exception.__class__):
        with log_and_raise(logger):
            raise original_exception

    logger.error.assert_called_once()

    call_args = logger.error.call_args.args
    assert len(call_args) == 1
    assert call_args[0] == str(original_exception)

    call_kwargs = logger.error.call_args.kwargs
    extra = call_kwargs["extra"]
    assert extra["raw_error_message"] == str(original_exception)
    assert extra["raw_error_class"] == original_exception.__class__.__name__


def test_simple_try_except_with_exception_override():
    logger: Any = Mock(spec=Logger)

    original_exception = ValueError("original exception")

    class CustomException(Exception):
        def __init__(self):
            super().__init__("custom exception")

    with pytest.raises(CustomException):
        with log_and_raise(logger, CustomException()):
            raise original_exception

    logger.error.assert_called_once()

    call_args = logger.error.call_args.args
    assert len(call_args) == 1
    assert call_args[0] == "custom exception"

    call_kwargs = logger.error.call_args.kwargs
    extra = call_kwargs["extra"]
    assert extra["raw_error_message"] == "custom exception"
    assert extra["raw_error_class"] == CustomException.__name__


def test_simple_try_except_with_extra_log_data():
    logger: Any = Mock(spec=Logger)

    original_exception = ValueError("original exception")

    class CustomException(Exception):
        def __init__(self):
            super().__init__("custom exception")

    with pytest.raises(CustomException):
        with log_and_raise(logger, CustomException(), extra_log_data={"extra": "data"}):
            raise original_exception

    call_kwargs = logger.error.call_args.kwargs
    extra = call_kwargs["extra"]
    assert extra["extra"] == "data"
