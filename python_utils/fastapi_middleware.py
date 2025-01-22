import json
import re
import time
import traceback
from typing import Awaitable, Callable, Optional, cast

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.concurrency import iterate_in_threadpool
from starlette.responses import StreamingResponse
from starlette.routing import Route

from python_utils.loggers import get_logger


logger = get_logger(__name__)


not_logged_path_checkers: list[Callable[[str], bool]] = [
    lambda path: path.endswith("/healthz"),
]


def should_log_path(path: str) -> bool:
    return not any(path_checker(path) for path_checker in not_logged_path_checkers)


def get_request_route_pattern(
    fastapi_app: FastAPI, request: Request, *, has_root_path: bool = False
) -> Optional[str]:
    for route in fastapi_app.router.routes:

        if not isinstance(route, Route):
            continue

        url_regex = route.path.replace("{", "(?P<").replace("}", ">[^/]+)")
        if has_root_path:
            root_path_regex = r"\/[a-zA-Z0-9\-\_]+"
            url_regex = root_path_regex + url_regex

        request_match_url_pattern = re.fullmatch(url_regex, request.url.path)

        if request_match_url_pattern:
            return route.path


def add_middleware(fastapi_app: FastAPI, has_root_path: bool = False) -> None:
    @fastapi_app.middleware("http")
    async def catch_exceptions(  # pyright: ignore[reportUnusedFunction]
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        log_path = should_log_path(request.url.path)

        if log_path:
            logger.info(
                "Request received",
                extra={
                    "request_path": request.url.path,
                    "request_path_pattern": get_request_route_pattern(
                        fastapi_app, request, has_root_path=has_root_path
                    ),
                    "request_method": request.method,
                    "query_params": request.query_params,
                    "headers": request.headers,
                },
            )

        start_time = time.time()

        try:
            response = cast(StreamingResponse, await call_next(request))
        except Exception as error:
            logger.critical(
                "Request failed",
                extra={"error": error, "traceback": traceback.format_exc()},
            )

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Unexpected server error"},
            )

        processing_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(processing_time)

        if log_path:
            # as `response` is a stream, we must deal with an iterator and reconstruct the body_iterator after it has been browsed
            # more details about the following code: https://github.com/encode/starlette/issues/874#issuecomment-1027743996
            response_body = [chunk async for chunk in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body))
            if len(response_body) == 0:
                parsed_response_body = None
            else:
                response_bytes = cast(bytes, response_body[0])
                try:
                    parsed_response_body = json.loads(response_bytes.decode())
                except json.JSONDecodeError:
                    parsed_response_body = None

            logger.info(
                "Request processed",
                extra={
                    "request_path": request.url.path,
                    "request_path_pattern": get_request_route_pattern(
                        fastapi_app, request, has_root_path=has_root_path
                    ),
                    "request_method": request.method,
                    "processing_time": processing_time,
                    "status_code": response.status_code,
                    "response_body": parsed_response_body,
                },
            )

        return response
