# Stubs missing for docker library
import docker  # pyright: ignore[reportMissingTypeStubs]
import os
import pytest

from python_utils.testing.docker import docker_compose_dir, start_service, stop_service


SERVICE_NAME = "hello_world"
DOCKER_COMPOSE_FILE = f"""
services:
  {SERVICE_NAME}:
    image: hello-world
"""


@pytest.fixture(scope="module")
def docker_compose_hello_dir():
    with docker_compose_dir(DOCKER_COMPOSE_FILE) as dir_path:
        yield dir_path


def test__start_service_container__success(docker_compose_hello_dir: str):
    start_service("hello_world", docker_compose_hello_dir)
    docker_client = docker.from_env() # pyright: ignore
    containers = docker_client.containers.list(all=True, filters={"name": SERVICE_NAME}) # pyright: ignore
    assert len(containers) == 1 # pyright: ignore
    stop_service("hello_world", docker_compose_hello_dir)


def test_docker_compose_dir():
    with docker_compose_dir(DOCKER_COMPOSE_FILE) as tmpdir:
        # Check if the directory exists
        assert os.path.isdir(tmpdir)

        # Check if the Docker Compose file exists in the temporary directory
        compose_file_path = os.path.join(tmpdir, "docker-compose.yml")
        assert os.path.isfile(compose_file_path)

        # Check if the content of the Docker Compose file is as expected
        with open(compose_file_path, "r") as f:
            content = f.read()
            assert content.strip() == DOCKER_COMPOSE_FILE.strip()

    # Check if the temporary directory is deleted after exiting the context manager
    assert not os.path.exists(tmpdir)
