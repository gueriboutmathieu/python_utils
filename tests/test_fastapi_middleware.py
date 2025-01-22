import pytest
from pytest import LogCaptureFixture
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Generator

from python_utils import (
    fastapi_middleware,
    fastapi_generic_routes,
)


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    fastapi_app = FastAPI()

    fastapi_middleware.add_middleware(fastapi_app)
    fastapi_generic_routes.load_routes(fastapi_app, "test_app", "1.2.3")

    @fastapi_app.get("/ressource/{ressource_id}")
    async def some_route(ressource_id: str):  # pyright: ignore[reportUnusedFunction]
        return {"ressource_id": ressource_id}

    test_client = TestClient(fastapi_app)

    yield test_client

    test_client.close()


@pytest.fixture
def test_client_with_root_path() -> Generator[TestClient, None, None]:
    fastapi_app = FastAPI()

    fastapi_middleware.add_middleware(
        fastapi_app, has_root_path=True
    )
    fastapi_generic_routes.load_routes(fastapi_app, "test_app", "1.2.3")

    @fastapi_app.get("/ressource/{ressource_id}")
    async def some_route(ressource_id: str):  # pyright: ignore[reportUnusedFunction]
        return {"ressource_id": ressource_id}

    test_client = TestClient(fastapi_app)

    yield test_client

    test_client.close()


def test_middleware_processing_time(test_client: TestClient):
    response = test_client.get("/")
    assert "X-Process-Time" in response.headers
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0.0


def test_middleware_exception_handling(test_client: TestClient):
    response = test_client.get("/force_exception")

    assert response.status_code == 500
    assert response.json() == {"message": "Unexpected server error"}


def test_log_url_pattern(caplog: LogCaptureFixture, test_client: TestClient):
    with caplog.at_level("INFO"):
        test_client.get("/ressource/1234")

    error_log_record = None
    for record in caplog.records:
        if record.message == "Request received":
            error_log_record = record
            break
    assert error_log_record is not None
    assert error_log_record.request_path_pattern == "/ressource/{ressource_id}"  # pyright: ignore


def test_log_url_pattern__with_root_path(
    caplog: LogCaptureFixture,
    test_client_with_root_path: TestClient
):
    with caplog.at_level("INFO"):
        test_client_with_root_path.get("/v1/ressource/1234")

    error_log_record = None
    for record in caplog.records:
        if record.message == "Request received":
            error_log_record = record
            break
    assert error_log_record is not None
    assert error_log_record.request_path_pattern == "/ressource/{ressource_id}"  # pyright: ignore
