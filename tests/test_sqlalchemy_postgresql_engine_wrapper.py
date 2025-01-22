import pytest

from python_utils.sqlalchemy_postgresql_engine_wrapper import SqlAlchemyPostgresqlEngineWrapper
from python_utils.testing.database import database_container
from python_utils.testing.docker import docker_compose_dir


DOCKER_COMPOSE_FILE = """
services:
  postgresql:
    image: bitnami/postgresql:14
    ports:
      - 55432:5432
    environment:
      - POSTGRESQL_USERNAME=user
      - POSTGRESQL_PASSWORD=password
      - POSTGRESQL_DATABASE=test_db
"""


@pytest.fixture(scope="module")
def setup_db():
    with docker_compose_dir(DOCKER_COMPOSE_FILE) as dir_path:
        with database_container(
            dir_path, "postgresql", "test_db", "user", "password", "localhost", 55432
        ):
            yield


def test__engine_wrapper_init_and_create_session(setup_db: None):
    engine_wrapper = SqlAlchemyPostgresqlEngineWrapper(
        sql_user="user",
        sql_password="password",
        sql_host="localhost",
        sql_port=55432,
        sql_database="test_db",
        pool_size=5,
    )

    session = engine_wrapper.create_session()
    # Assert that the session is created
    assert session is not None
