from uuid import UUID
import pytest

from logging import Logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Mapped, mapped_column, Session, sessionmaker
from typing import Type
from uuid6 import uuid7

from python_utils.entity import Entity
from python_utils.loggers import get_logger
from python_utils.sqlalchemy_crud_repository import SQLAlchemyCRUDRepository
from python_utils.testing.database import database_container
from python_utils.testing.docker import docker_compose_dir


@pytest.fixture
def logger():
    logger = get_logger(__name__)
    yield logger


class TestEntity(Entity):
    __tablename__ = "test_table"

    id: Mapped[UUID] = mapped_column(init=True, primary_key=True)
    name: Mapped[str] = mapped_column(init=True)


class DefaultException(Exception):
    pass


class NotFoundException(Exception):
    pass


class ConstraintException(Exception):
    pass


class TestCrudRepository(SQLAlchemyCRUDRepository[TestEntity]):
    def __init__(
        self,
        session: Session,
        entity_class: Type[TestEntity],
        logger: Logger,
        default_exception: Type[Exception],
        not_found_exception: Type[Exception],
        constraint_exception: Type[Exception],
    ):
        super().__init__(
            session=session,
            entity_class=entity_class,
            logger=logger,
            default_exception=default_exception,
            not_found_exception=not_found_exception,
            constraint_exception=constraint_exception,
        )


@pytest.fixture
def test_crud_repository(session: Session, logger: Logger):
    return TestCrudRepository(
        session=session,
        entity_class=TestEntity,
        logger=logger,
        default_exception=DefaultException,
        not_found_exception=NotFoundException,
        constraint_exception=ConstraintException,
    )


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


@pytest.fixture
def session(setup_db: None):
    engine = create_engine("postgresql+psycopg2://user:password@localhost:55432/test_db")

    print("Creating tables")
    TestEntity.metadata.create_all(engine)

    session = sessionmaker(engine)()

    yield session

    session.close()
    print("Dropping tables")
    TestEntity.metadata.drop_all(session.connection().engine)


def test_create_and_get_entity(test_crud_repository: TestCrudRepository):
    new_test_entity = TestEntity(id=uuid7(), name="test_entity")
    test_crud_repository.create(new_test_entity)
    test_crud_repository.session.commit()

    test_entity = test_crud_repository.get(new_test_entity.id)
    assert test_entity is not None
    assert test_entity.id == new_test_entity.id
    assert test_entity.name == new_test_entity.name


def test_create_entity_constraint_exception(test_crud_repository: TestCrudRepository):
    uuid = uuid7()
    name = "test_entity"
    new_test_entity = TestEntity(id=uuid, name=name)
    test_crud_repository.create(new_test_entity)
    test_crud_repository.session.commit()

    duplicated_test_entity = TestEntity(id=uuid, name=name)
    with pytest.raises(ConstraintException):
        test_crud_repository.create(duplicated_test_entity)


def test_get_or_raise_entity_not_found_exception(test_crud_repository: TestCrudRepository):
    with pytest.raises(NotFoundException):
        test_crud_repository.get_or_raise(uuid7())


def test_update_entity(test_crud_repository: TestCrudRepository):
    new_test_entity = TestEntity(id=uuid7(), name="test_entity")
    test_crud_repository.create(new_test_entity)
    test_crud_repository.session.commit()

    updated_entity = TestEntity(id=new_test_entity.id, name="updated_test_entity")
    test_crud_repository.update(new_test_entity.id, updated_entity)
    test_crud_repository.session.commit()

    test_entity = test_crud_repository.get(new_test_entity.id)
    assert test_entity is not None
    assert test_entity.id == new_test_entity.id
    assert test_entity.name == updated_entity.name


def test_update_entity_not_found_exception(test_crud_repository: TestCrudRepository):
    with pytest.raises(NotFoundException):
        test_crud_repository.update(uuid7(), TestEntity(id=uuid7(), name="test_entity"))


def test_update_entity_constraint_exception(test_crud_repository: TestCrudRepository):
    uuid = uuid7()
    name = "test_entity"
    new_test_entity = TestEntity(id=uuid, name=name)
    test_crud_repository.create(new_test_entity)
    test_crud_repository.session.commit()

    new_test_entity_2 = TestEntity(id=uuid7(), name="test_entity_2")
    test_crud_repository.create(new_test_entity_2)
    test_crud_repository.session.commit()

    with pytest.raises(ConstraintException):
        test_crud_repository.update(new_test_entity_2.id, TestEntity(id=uuid, name=name))


def test_delete_entity(test_crud_repository: TestCrudRepository):
    new_test_entity = TestEntity(id=uuid7(), name="test_entity")
    test_crud_repository.create(new_test_entity)
    test_crud_repository.session.commit()

    test_crud_repository.delete(new_test_entity.id)
    test_crud_repository.session.commit()

    test_entity = test_crud_repository.get(new_test_entity.id)
    assert test_entity is None

    with pytest.raises(NotFoundException):
        test_crud_repository.get_or_raise(new_test_entity.id)


def test_delete_entity_not_found_exception(test_crud_repository: TestCrudRepository):
    with pytest.raises(NotFoundException):
        test_crud_repository.delete(uuid7())
