from python_utils.paths import get_repository_root_path


def test__get_repository_root_path__success():
    root_path = get_repository_root_path(__file__)
    directory_name = root_path.split("/")[-1]
    assert directory_name == "python_utils"
