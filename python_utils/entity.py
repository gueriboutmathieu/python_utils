from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Entity(MappedAsDataclass, DeclarativeBase):
    pass
