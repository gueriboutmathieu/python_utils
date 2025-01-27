from _typeshed import Incomplete
from fastapi import FastAPI as FastAPI, Request as Request, Response as Response
from python_utils.loggers import get_logger as get_logger
from typing import Callable

logger: Incomplete
not_logged_path_checkers: list[Callable[[str], bool]]

def should_log_path(path: str) -> bool: ...
def get_request_route_pattern(fastapi_app: FastAPI, request: Request, *, has_root_path: bool = False) -> str | None: ...
def add_middleware(fastapi_app: FastAPI, has_root_path: bool = False) -> None: ...
