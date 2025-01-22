# Stubs missing for docker library
import docker  # pyright: ignore[reportMissingTypeStubs]
import psycopg2
import pytest
import sqlalchemy as sa
from dataclasses import dataclass
from sqlalchemy import Column, create_engine
from sqlalchemy.dialects.postgresql import UUID as sa_UUID
from sqlalchemy.orm import registry, sessionmaker
from sqlalchemy.pool import QueuePool
from uuid import UUID
from uuid6 import uuid7

from python_utils.testing.database import (
    database_container,
    reset_sqlalchemy_model_table,
    wait_for_db_to_be_ready,
)
from python_utils.testing.docker import docker_compose_dir


SERVICE_NAME = "postgresql"
USER = "user"
PASSWORD = "password"
HOST = "localhost"
PORT = 55432
DB_NAME = "test_db"


DOCKER_COMPOSE_FILE = f"""
services:
  {SERVICE_NAME}:
    image: bitnami/postgresql:14
    ports:
      - {PORT}:5432
    environment:
      - POSTGRESQL_USERNAME={USER}
      - POSTGRESQL_PASSWORD={PASSWORD}
      - POSTGRESQL_DATABASE={DB_NAME}
"""


@pytest.fixture
def setup_db():
    with docker_compose_dir(DOCKER_COMPOSE_FILE) as dir_path:
        with database_container(
            dir_path, SERVICE_NAME, DB_NAME, USER, PASSWORD, HOST, PORT
        ):
            yield


def test__wait_for_db_to_be_ready(setup_db: None):
    wait_for_db_to_be_ready(
        db_name=DB_NAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
    )


def test__wait_for_db_to_be_ready__timeout():
    with pytest.raises(Exception, match="Could not connect to db after 2 attempts"):
        wait_for_db_to_be_ready(DB_NAME, USER, PASSWORD, HOST, PORT, max_attempts=2)
        # Assert that psycopg2.connect was called the correct number of times
        assert psycopg2.connect.call_count == 2  # pyright: ignore


def test__database_container():
    docker_client = docker.from_env()  # pyright: ignore
    # Check if the container doesn't exist initially
    containers = docker_client.containers.list(all=True, filters={"name": SERVICE_NAME})  # pyright: ignore
    assert len(containers) == 0  # pyright: ignore

    with docker_compose_dir(DOCKER_COMPOSE_FILE) as dir_path:
        with database_container(
            dir_path, SERVICE_NAME, DB_NAME, USER, PASSWORD, HOST, PORT
        ):
            # Check if the container exists during the context manager's scope
            containers = docker_client.containers.list(  # pyright: ignore
                all=True, filters={"name": SERVICE_NAME}
            )
            assert len(containers) == 1  # pyright: ignore

    # Check if the container is stopped after exiting the context manager
    containers = docker_client.containers.list(all=True, filters={"name": SERVICE_NAME})  # pyright: ignore
    assert len(containers) == 0  # pyright: ignore


@dataclass
class TestEntity:
    id: UUID


def test__reset_sqlalchemy_model_table(setup_db: None):
    engine = create_engine(
        f"{SERVICE_NAME}+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}",
        poolclass=QueuePool,
        pool_size=5,
    )

    mapper_registry = registry()
    test_table = sa.Table(
        "test_table",
        mapper_registry.metadata,
        Column("id", sa_UUID(as_uuid=True), primary_key=True),
    )
    mapper_registry.map_imperatively(TestEntity, test_table)

    # Create the table in the database
    mapper_registry.metadata.create_all(engine, tables=[test_table])

    # Add a row to the table
    session = sessionmaker(engine)()
    test_id = uuid7()
    session.add(TestEntity(id=test_id))
    session.commit()

    result = session.get(TestEntity, test_id)
    assert result is not None
    assert result.id == test_id
    session.close()

    # Reset the model
    reset_sqlalchemy_model_table(engine, TestEntity)

    # Assert that the table is empty
    new_session = sessionmaker(engine)()

    result = new_session.get(TestEntity, test_id)
    assert result is None
    new_session.close()
