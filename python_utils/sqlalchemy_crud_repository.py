import traceback

from dataclasses import fields
from logging import Logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Generic, Optional, Type, TypeVar
from uuid import UUID

from python_utils.entity import Entity


TypeEntity = TypeVar("TypeEntity", bound=Entity)


class SQLAlchemyCRUDRepository(Generic[TypeEntity]):
    def __init__(
        self,
        session: Session,
        entity_class: Type[TypeEntity],
        logger: Logger,
        default_exception: Type[Exception],
        not_found_exception: Optional[Type[Exception]] = None,
        constraint_exception: Optional[Type[Exception]] = None,
    ):
        self.session = session
        self.entity_class = entity_class
        self.logger = logger
        self.default_exception = default_exception
        self.not_found_exception = not_found_exception
        self.constraint_exception = constraint_exception

    def create(self, entity: TypeEntity) -> None:
        try:
            self.session.add(entity)
            self.session.flush()
        except IntegrityError:
            exception = (
                self.constraint_exception()
                if self.constraint_exception is not None
                else self.default_exception()
            )
            self.logger.exception(
                str(exception),
                extra={"traceback": traceback.format_exc()},
            )
            raise exception
        except Exception as raw_exception:
            exception = self.default_exception()

            self.logger.exception(
                str(exception),
                extra={
                    "raw_exception": raw_exception,
                    "exception_class": raw_exception.__class__.__name__,
                    "traceback": traceback.format_exc(),
                },
            )
            raise exception

    def get(self, entity_id: UUID) -> Optional[TypeEntity]:
        entity = self.session.get(self.entity_class, entity_id)
        return entity

    def get_or_raise(self, entity_id: UUID) -> TypeEntity:
        entity = self.get(entity_id)
        if entity is None:
            exception = (
                self.not_found_exception()
                if self.not_found_exception is not None
                else self.default_exception()
            )
            self.logger.exception(
                str(exception),
                extra={
                    "entity_id": entity_id,
                    "traceback": traceback.format_exc(),
                },
            )
            raise exception
        return entity


    def update(self, entity_id: UUID, new_entity: TypeEntity) -> None:
        entity = self.get_or_raise(entity_id)
        attribute_names = [field.name for field in fields(new_entity)]
        try:
            for attribute_name in attribute_names:
                setattr(
                    entity, attribute_name, getattr(new_entity, attribute_name)
                )
            self.session.flush()
        except IntegrityError:
            exception = (
                self.constraint_exception()
                if self.constraint_exception is not None
                else self.default_exception()
            )
            self.logger.exception(
                str(exception),
                extra={"traceback": traceback.format_exc()},
            )
            raise exception
        except Exception as raw_exception:
            exception = self.default_exception()

            self.logger.exception(
                str(exception),
                extra={
                    "raw_exception": raw_exception,
                    "exception_class": raw_exception.__class__.__name__,
                    "traceback": traceback.format_exc(),
                },
            )
            raise exception

    def delete(self, entity_id: UUID) -> None:
        entity = self.get_or_raise(entity_id)
        try:
            self.session.delete(entity)
        except Exception as raw_exception:
            exception = self.default_exception()

            self.logger.exception(
                str(exception),
                extra={
                    "raw_exception": raw_exception,
                    "exception_class": raw_exception.__class__.__name__,
                    "traceback": traceback.format_exc(),
                },
            )
            raise exception
