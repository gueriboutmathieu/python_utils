import time
import traceback

from typing import Callable, Concatenate, Generic, ParamSpec, Protocol, TypeVar

from python_utils.loggers import get_logger

logger = get_logger(__name__, indent=4)


class CommandContext(Protocol):
    def rollback(self) -> None: ...

    def commit(self) -> None: ...


CC = TypeVar("CC", bound=CommandContext)
P = ParamSpec("P")
R = TypeVar("R")

CommandContextCreator = Callable[[], CC]


class Domain(Generic[CC]):
    def __init__(self, command_context_creator: CommandContextCreator[CC]) -> None:
        self.command_context_creator = command_context_creator

    def _bind_command(
        self,
        command: Callable[Concatenate[CC, P], R],
    ) -> Callable[P, R]:
        def bound_command(*args: P.args, **kwargs: P.kwargs) -> R:
            logger.debug(
                "Command about to be called",
                extra={
                    "command_name": command.__name__,
                    "command_args": args,
                    "command_kwargs": kwargs,
                },
            )

            start_time = time.time()

            command_context = self.command_context_creator()

            # Attempt to execute the command
            try:
                result = command(command_context, *args, **kwargs)

            # Catch any exception raised during command execution
            except Exception as original_execution_exception:
                logger.error(
                    "An unexpected error occurred during command execution, rollback will be applied.",
                    extra={
                        "error": str(original_execution_exception),
                        "error_class": original_execution_exception.__class__.__name__,
                        "traceback": traceback.format_exc(),
                    },
                )

                # Attempt to rollback the command
                try:
                    command_context.rollback()

                # Catch any exception raised during command rollback
                except Exception as original_rollback_exception:
                    logger.error(
                        "An unexpected error occurred during command rollback",
                        extra={
                            "error": str(original_rollback_exception),
                            "error_class": original_rollback_exception.__class__.__name__,
                            "traceback": traceback.format_exc(),
                        },
                    )

                    # Set the CommandExecutionException as context of the original_rollback_exception
                    original_rollback_exception.__cause__ = original_execution_exception
                    # Raise a new CommandRollbackException, using the original_rollback_exception as context
                    raise CommandRollbackException() from original_rollback_exception

                raise original_execution_exception

            # Attempt to commit the command
            try:
                command_context.commit()
            # Catch any exception raised during command commit
            except Exception as original_commit_exception:
                logger.error(
                    "An unexpected error occurred during command commit",
                    extra={
                        "error": str(original_commit_exception),
                        "error_class": original_commit_exception.__class__.__name__,
                        "traceback": traceback.format_exc(),
                    },
                )

                # Attempt to rollback the command
                try:
                    command_context.rollback()
                    # Catch any exception raised during command rollback
                except Exception as original_rollback_exception:
                    logger.error(
                        "An unexpected error occurred during command rollback after a commit failed",
                        extra={
                            "error": str(original_rollback_exception),
                            "error_class": original_rollback_exception.__class__.__name__,
                            "traceback": traceback.format_exc(),
                        },
                    )

                    # Set the CommandExecutionException as context of the original_rollback_exception
                    original_rollback_exception.__cause__ = original_commit_exception
                    # Raise a new CommandRollbackException, using the original_rollback_exception as context
                    raise CommandRollbackException() from original_rollback_exception

                # Create a new CommandCommitException to be raised, using the original exception as context
                raise CommandCommitException() from original_commit_exception

            duration = time.time() - start_time

            logger.debug(
                "Command returned",
                extra={
                    "command_name": command.__name__,
                    "result": result,
                    "duration": duration,
                },
            )
            return result

        return bound_command


class CommandRollbackException(Exception):
    def __init__(self):
        super().__init__("Error during the rollback of a command")


class CommandCommitException(Exception):
    def __init__(self):
        super().__init__("Error during the commit of a command")
