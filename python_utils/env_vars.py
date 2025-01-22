import os
from dotenv import load_dotenv
from typing import Any, Callable, Generic, TypeVar, Union


load_dotenv(override=True)


T = TypeVar("T")
CastFunction = Callable[[str], T]


class Unset:
    pass


UNSET = Unset()


class EnvVar(Generic[T]):
    value: T

    def __init__(
        self: Any,
        name: str,
        cast_fct: CastFunction[T],
        default: Union[T, Unset] = UNSET,
    ):
        # get value from env
        raw_value = os.getenv(name)

        # use default if there is one and no raw_value is found in env, else raise exception
        if raw_value is None:
            if isinstance(default, Unset):
                raise ValueError(f'Missing required environment variable "{name}"')
            self.value = default
            return

        # attempt to cast the value
        try:
            cast_value = cast_fct(raw_value)
        except Exception as e:
            raise Exception("An error occurred when casting the value") from e

        self.value = cast_value
