import contextlib
import os


@contextlib.contextmanager
def set_working_directory(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No such file or directory: '{path}'")
    old_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)
