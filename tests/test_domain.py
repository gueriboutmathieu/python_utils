import pytest
from pytest_mock import MockerFixture
from typing import Any, Protocol


from python_utils.domain import (
    Domain,
    CommandCommitException,
    CommandContextCreator,
    CommandRollbackException,
    CommandContext,
)


class DomainCommandContext(CommandContext, Protocol):
    pass


class ConcreteCommandContext:
    def rollback(self) -> None:
        pass

    def commit(self) -> None:
        pass


class DomainForTesting(Domain[ConcreteCommandContext]):
    def __init__(
        self,
        command: Any,
        command_context_creator: CommandContextCreator[ConcreteCommandContext],
    ) -> None:
        super().__init__(command_context_creator)

        self.some_command = self._bind_command(command)


def test__command_commit(mocker: MockerFixture):
    command_context = ConcreteCommandContext()
    mocker.patch.object(command_context, "commit")
    mocker.patch.object(command_context, "rollback")

    def some_command(_: ConcreteCommandContext):
        pass

    domain = DomainForTesting(some_command, lambda: command_context)
    domain.some_command()  # pyright: ignore

    command_context.commit.assert_called_once()  # pyright: ignore
    command_context.rollback.assert_not_called()  # pyright: ignore


def test__command_rollback(mocker: MockerFixture):
    command_context = ConcreteCommandContext()
    mocker.patch.object(command_context, "commit")
    mocker.patch.object(command_context, "rollback")

    def some_command(_: ConcreteCommandContext):
        raise Exception("Some command exception")

    domain = DomainForTesting(some_command, lambda: command_context)
    with pytest.raises(Exception) as exception_info:
        domain.some_command()  # pyright: ignore

    assert str(exception_info.value) == "Some command exception"

    command_context.commit.assert_not_called()  # pyright: ignore
    command_context.rollback.assert_called_once()  # pyright: ignore


def test__command_commit_failed(mocker: MockerFixture):
    command_context = ConcreteCommandContext()
    mocker.patch.object(
        command_context, "commit", side_effect=Exception("Some commit exception")
    )
    mocker.patch.object(command_context, "rollback")

    def some_command(_: ConcreteCommandContext):
        pass

    domain = DomainForTesting(some_command, lambda: command_context)
    with pytest.raises(CommandCommitException) as exception_info:
        domain.some_command()  # pyright: ignore

    original_exception = exception_info.value.__cause__
    assert str(original_exception) == "Some commit exception"

    command_context.commit.assert_called_once()  # pyright: ignore
    command_context.rollback.assert_called_once()  # pyright: ignore


def test__command_rollback_failed(mocker: MockerFixture):
    command_context = ConcreteCommandContext()
    mocker.patch.object(command_context, "commit")
    mocker.patch.object(
        command_context, "rollback", side_effect=Exception("Some rollback exception")
    )

    def some_command(_: ConcreteCommandContext):
        raise Exception("Some command exception")

    domain = DomainForTesting(some_command, lambda: command_context)
    with pytest.raises(CommandRollbackException) as exception_info:
        domain.some_command()  # pyright: ignore

    original_exception = exception_info.value.__cause__
    assert str(original_exception) == "Some rollback exception"
    original_original_exception = (original_exception.__cause__)  # pyright: ignore
    assert str(original_original_exception) == "Some command exception"

    command_context.commit.assert_not_called()  # pyright: ignore
    command_context.rollback.assert_called_once()  # pyright: ignore
