import re
from os import urandom
from pathlib import Path

import pytest
from yaml.parser import ParserError

from whispers import core

from .conftest import FIXTURE_PATH, config_path, fixture_path


@pytest.mark.parametrize(
    ("filename", "exception"),
    [(f"/tmp/File404-{urandom(30).hex()}", FileNotFoundError), ("/dev/null", TypeError)],
)
def test_core_exception(filename, exception):
    with pytest.raises(exception):
        next(core.run(filename))


def test_load_config_exception():
    with pytest.raises(ParserError):
        core.load_config(config_path("invalid.yml"), FIXTURE_PATH)


def test_load_config():
    config = core.load_config(config_path("example.yml"), FIXTURE_PATH)
    assert set(config["exclude"]["files"]) == set(
        [
            Path(fixture_path(".npmrc")),
            Path(fixture_path("hardcoded.json")),
            Path(fixture_path("hardcoded.yml")),
            Path(fixture_path("hardcoded.xml")),
        ]
    )
    assert config["exclude"]["keys"] == [re.compile("SECRET_VALUE_KEY", flags=re.IGNORECASE)]
    assert config["exclude"]["values"] == [re.compile("SECRET_VALUE_PLACEHOLDER", flags=re.IGNORECASE)]


def test_include_files():
    config = core.load_config(config_path("include_files.yml"), FIXTURE_PATH)
    secrets = core.run(FIXTURE_PATH, config=config)
    assert next(secrets).value == "hardcoded"
    with pytest.raises(StopIteration):
        next(secrets)


def test_exclude_files():
    config = core.load_config(config_path("exclude_files.yml"), FIXTURE_PATH)
    secrets = core.run(FIXTURE_PATH, config=config)
    with pytest.raises(StopIteration):
        next(secrets)
