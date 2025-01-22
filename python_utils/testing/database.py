import alembic.config
import contextlib
import psycopg2
import time
from sqlalchemy import delete
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
from typing import Type

from python_utils.entity import Entity
from python_utils.testing.directory import set_working_directory
from python_utils.testing.docker import start_service, stop_service


def wait_for_db_to_be_ready(
    db_name: str, user: str, password: str, host: str, port: int, max_attempts: int = 20
) -> None:
    print("Waiting for db to be ready...")
    for counter in range(max_attempts):
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port,
                connect_timeout=1,
            )
            conn.close()
            return
        except Exception as e:
            if counter == max_attempts - 1:
                raise Exception(
                    f"Could not connect to db after {max_attempts} attempts"
                ) from e
            time.sleep(1)


def run_alembic_migrations(work_dir: str) -> None:
    print("Running db migrations...")
    with set_working_directory(work_dir):
        alembic.config.main(  # pyright: ignore[reportUnknownMemberType]
            argv=["upgrade", "head"]
        )


def reset_sqlalchemy_model_table(engine: Engine, entity: Type[Entity]) -> None:
    print(f"Emptying table {entity.__name__}...")
    with Session(engine) as session:
        # Delete all rows from the table
        session.execute(delete(entity))
        session.commit()


@contextlib.contextmanager
def database_container(
    docker_compose_psql_dir: str,
    service_name: str,
    db_name: str,
    user: str,
    password: str,
    host: str,
    port: int,
):
    start_service(service_name, docker_compose_psql_dir)
    wait_for_db_to_be_ready(db_name, user, password, host, port)

    yield

    stop_service(service_name, docker_compose_psql_dir)
