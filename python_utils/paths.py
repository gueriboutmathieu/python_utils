import pathlib
from typing import Union


def get_repository_root_path(path: Union[pathlib.Path, str]) -> str:
    path = pathlib.Path(path)

    if path.is_file():
        directory_path = path.parent
    else:
        directory_path = path

    if not pathlib.Path(f"{directory_path}/.git").is_dir():
        parent_directory_path = directory_path.parent
        if parent_directory_path == directory_path:
            raise ValueError("Given path does not seem to be in a git repository")
        directory_path = get_repository_root_path(parent_directory_path)

    return str(directory_path)
