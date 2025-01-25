import contextlib
import os
import subprocess
import tempfile

from python_utils.testing.directory import set_working_directory


def start_service(service_name: str, workdir: str) -> None:
    with set_working_directory(workdir):
        print(f"Starting service {service_name}...")
        try:
            subprocess.check_output(
                f"docker compose up -d {service_name}",
                stderr=subprocess.STDOUT,
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            print(e.stdout.decode("utf-8"))
            raise


def stop_service(service_name: str, workdir: str) -> None:
    with set_working_directory(workdir):
        print(f"Stopping and removing service {service_name}...")
        try:
            subprocess.check_output(
                f"docker compose down {service_name} --volumes --remove-orphans",
                stderr=subprocess.STDOUT,
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            print(e.stdout.decode("utf-8"))
            raise


@contextlib.contextmanager
def docker_compose_dir(docker_compose_file_content: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "docker-compose.yaml"), "w") as f:
            f.write(docker_compose_file_content)

        yield tmpdir
