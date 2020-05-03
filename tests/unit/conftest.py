from contextlib import contextmanager
from pathlib import Path

FIXTURE_PATH = Path("tests/fixtures")
CONFIG_PATH = Path("tests/configs")
RULE_PATH = Path("tests/rules")


@contextmanager
def does_not_raise():
    yield


def fixture_path(filename: str) -> str:
    return FIXTURE_PATH.joinpath(filename).as_posix()


def config_path(filename: str) -> str:
    return CONFIG_PATH.joinpath(filename).as_posix()


def rule_path(filename: str) -> str:
    return RULE_PATH.joinpath(filename).as_posix()
