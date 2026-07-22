from importlib.metadata import version


def test_package_is_installed():
    assert version("dailoqa-backend") == "0.1.0"
