import re
from os import urandom
from pathlib import Path

import pytest
from yaml.parser import ParserError

from tests.unit.conftest import FIXTURE_PATH, config_path, does_not_raise, fixture_path
from whispers import core
from whispers.cli import parse_args


@pytest.mark.parametrize(
    ("filename", "expectation"),
    [
        (f"/tmp/File404-{urandom(30).hex()}", pytest.raises(FileNotFoundError)),
        ("/dev/null", pytest.raises(TypeError)),
        (fixture_path("hardcoded.yml"), does_not_raise()),
    ],
)
def test_run(filename, expectation):
    with expectation:
        args = parse_args([filename])
        next(core.run(args))


@pytest.mark.parametrize(
    ("filename", "expectation"),
    [
        (f"/tmp/File404-{urandom(30).hex()}", pytest.raises(FileNotFoundError)),
        ("/dev/null", pytest.raises(TypeError)),
        (config_path("invalid.yml"), pytest.raises(ParserError)),
        (config_path("empty.yml"), pytest.raises(NameError)),
        (config_path("example.yml"), does_not_raise()),
    ],
)
def test_load_config_exception(filename, expectation):
    with expectation:
        core.load_config(filename, FIXTURE_PATH)


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
