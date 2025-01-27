from _typeshed import Incomplete
from python_utils.loggers import get_logger as get_logger
from typing import Callable, Concatenate, Generic, ParamSpec, Protocol, TypeVar

logger: Incomplete

class CommandContext(Protocol):
    def rollback(self) -> None: ...
    def commit(self) -> None: ...
CC = TypeVar('CC', bound=CommandContext)
P = ParamSpec('P')
R = TypeVar('R')
CommandContextCreator = Callable[[], CC]

class Domain(Generic[CC]):
    command_context_creator: Incomplete
    def __init__(self, command_context_creator: CommandContextCreator[CC]) -> None: ...
    def _bind_command(self, command: Callable[Concatenate[CC, P], R]) -> Callable[P, R]: ...

class CommandRollbackException(Exception):
    def __init__(self) -> None: ...

class CommandCommitException(Exception):
    def __init__(self) -> None: ...
