import contextlib
import os
import requests
import socket
import subprocess
import sys
import time
from typing import Any


def run_in_subprocess(
    command: str, env: dict[str, Any] = {}
) -> subprocess.Popen[bytes]:
    print(f"Starting subprocess with command '{command}' ...")
    return subprocess.Popen(
        command,
        stdout=sys.stdout,
        stderr=sys.stderr,
        shell=True,
        env=env,
    )


@contextlib.contextmanager
def run_web_server(server_file_path: str, max_check_health_attempts: int = 10):
    print(f"Starting server in {server_file_path}...")
    port = get_next_available_port()
    server_import_path = server_file_path.replace(".py", "").replace("/", ".")

    process = run_in_subprocess(
        f"uvicorn --port {port} {server_import_path}:app",
        env=os.environ.copy(),
    )

    url = f"http://localhost:{port}"

    wait_for_server_to_be_ready(url, max_check_health_attempts)

    yield url

    process.kill()


def get_next_available_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 50000
    while port <= 65535:
        try:
            sock.bind(("", port))
            sock.close()
            return port
        except OSError:
            port += 1
    raise IOError("no free ports")


def wait_for_server_to_be_ready(url: str, max_attempts: int):
    print(f"Waiting for server at {url} to be ready...")
    for _ in range(max_attempts):
        try:
            requests.get(url)
            return
        except Exception:
            time.sleep(1)
    raise Exception(f"Could not connect to {url} after {max_attempts} attempts")
