from _typeshed import Incomplete
from typing import Callable, Generic, TypeVar

T = TypeVar('T')
CastFunction = Callable[[str], T]

class Unset: ...

UNSET: Incomplete

class EnvVar(Generic[T]):
    value: T
    def __init__(self, name: str, cast_fct: CastFunction[T], default: T | Unset = ...) -> None: ...
