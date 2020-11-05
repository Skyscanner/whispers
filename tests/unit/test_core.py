import re
from os import urandom
from pathlib import Path

import pytest
from yaml.parser import ParserError

from whispers import core
from whispers.cli import parse_args

from .conftest import FIXTURE_PATH, config_path, fixture_path


@pytest.mark.parametrize(
    ("filename", "exception"),
    [(f"/tmp/File404-{urandom(30).hex()}", FileNotFoundError), ("/dev/null", TypeError)],
)
def test_core_exception(filename, exception):
    with pytest.raises(exception):
        args = parse_args([filename])
        next(core.run(args))


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
    args = parse_args([fixture_path()])
    args.config = core.load_config(config_path("include_files.yml"), FIXTURE_PATH)
    secrets = core.run(args)
    assert next(secrets).value == "hardcoded"
    with pytest.raises(StopIteration):
        next(secrets)


def test_exclude_files():
    args = parse_args([fixture_path()])
    args.config = core.load_config(config_path("exclude_files.yml"), FIXTURE_PATH)
    secrets = core.run(args)
    with pytest.raises(StopIteration):
        next(secrets)
