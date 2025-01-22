import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Generator

from python_utils import fastapi_generic_routes


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    app = FastAPI()

    fastapi_generic_routes.load_routes(app, "test_app", "1.2.3")

    test_client = TestClient(app)

    yield test_client

    test_client.close()


def test_root_endpoint(test_client: TestClient):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "application_name": "test_app",
        "client_ip": "testclient",
        "version": "1.2.3",
    }


def test_health_endpoint(test_client: TestClient):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "It's alive!"}
    assert "X-App-Alive" in response.headers


def test_force_exception_endpoint(test_client: TestClient):
    with pytest.raises(Exception):
        test_client.get("/force_exception")
