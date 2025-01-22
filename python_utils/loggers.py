import contextlib
import functools
import logging
import traceback
from pythonjsonlogger.json import JsonFormatter
from typing import Any, Generator, Optional


global_stdout_log_level: Optional[int] = None


@functools.cache
def get_stdout_handler(log_level: int, log_formatter: logging.Formatter):
    handler = logging.StreamHandler()
    handler.setFormatter(log_formatter)
    handler.setLevel(log_level)

    return handler


class CustomJsonFormatter(JsonFormatter):
    def __init__(
        self,
        *args: Any,
        add_context_fields: bool = True,
        indent: Optional[int] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs, json_indent=indent)  # pyright: ignore
        self.add_context_fields = add_context_fields

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ):
        super().add_fields(log_record, record, message_dict)

        log_data = {
            "time": self.formatTime(record),
            "timestamp": record.created,
        }

        if self.add_context_fields:
            log_data.update(
                {
                    "level": record.levelname,
                    "logger_name": record.name,
                    "line": record.lineno,
                }
            )
        log_record.update(log_data)


@functools.cache
def get_logger(
    name: str,
    stdout_log_level: Optional[int] = None,
) -> logging.Logger:
    stdout_log_level = global_stdout_log_level or logging.INFO

    logger = logging.getLogger(name)

    # As log levels are set on handlers directly, logger log level is set
    # to DEBUG to make sure log events reach the handlers
    logger.setLevel("DEBUG")

    stdout_handler = get_stdout_handler(stdout_log_level, CustomJsonFormatter())
    logger.addHandler(stdout_handler)

    return logger


@contextlib.contextmanager
def log_and_raise(
    logger: logging.Logger,
    exception_to_raise: Optional[Exception] = None,
    extra_log_data: dict[str, Any] = {},
) -> Generator[None, None, None]:
    try:
        yield
    except Exception as raw_exception:
        exception = exception_to_raise or raw_exception

        logger.error(
            str(exception),
            extra={
                "raw_error_message": str(exception),
                "raw_error_class": exception.__class__.__name__,
                "traceback": traceback.format_exc(),
                **extra_log_data,
            },
        )
        raise exception
