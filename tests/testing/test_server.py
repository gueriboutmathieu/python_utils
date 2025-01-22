import os
import tempfile

import pytest
import requests

from python_utils.testing.server import run_web_server

PYTHON_SERVER_FILE = """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
"""


@pytest.fixture
def python_server_file_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a server file in a modue in the temp dir
        server_module_path = os.path.join(tmp_dir, "server_module")
        os.mkdir(server_module_path)
        server_file_path = os.path.join(server_module_path, "server.py")
        with open(server_file_path, "w") as f:
            f.write(PYTHON_SERVER_FILE)

        # Add the temp dir to the PYTHONPATH
        original_python_path = os.environ.get("PYTHONPATH")
        if original_python_path:
            new_python_path = f"{tmp_dir}:{original_python_path}"
        else:
            new_python_path = tmp_dir
        os.environ["PYTHONPATH"] = new_python_path

        # The path to the server file absolute path to relative path
        server_relative_file_path = os.path.join("server_module", "server.py")

        yield server_relative_file_path


def test__run_web_server__success(python_server_file_path: str):
    with run_web_server(python_server_file_path) as url:
        response = requests.get(url)
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}
