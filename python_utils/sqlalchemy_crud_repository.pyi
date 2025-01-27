from _typeshed import Incomplete
from logging import Logger
from python_utils.entity import Entity as Entity
from sqlalchemy.orm import Session as Session
from typing import Generic, TypeVar
from uuid import UUID

TypeEntity = TypeVar('TypeEntity', bound=Entity)

class SQLAlchemyCRUDRepository(Generic[TypeEntity]):
    session: Incomplete
    entity_class: Incomplete
    logger: Incomplete
    default_exception: Incomplete
    not_found_exception: Incomplete
    constraint_exception: Incomplete
    def __init__(self, session: Session, entity_class: type[TypeEntity], logger: Logger, default_exception: type[Exception], not_found_exception: type[Exception] | None = None, constraint_exception: type[Exception] | None = None) -> None: ...
    def create(self, entity: TypeEntity) -> None: ...
    def get(self, entity_id: UUID) -> TypeEntity | None: ...
    def get_or_raise(self, entity_id: UUID) -> TypeEntity: ...
    def update(self, entity_id: UUID, new_entity: TypeEntity) -> None: ...
    def delete(self, entity_id: UUID) -> None: ...
