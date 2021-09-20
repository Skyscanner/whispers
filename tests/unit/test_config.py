import re
from os import urandom

import pytest
from yaml.parser import ParserError

from tests.unit.conftest import config_path, does_not_raise
from whispers.core.args import parse_args
from whispers.core.config import default_config_structure, load_config
from whispers.core.rules import default_rules, list_rule_ids


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        (f"/tmp/File404-{urandom(30).hex()}", pytest.raises(FileNotFoundError)),
        ("/dev/null", pytest.raises(TypeError)),
        (config_path("invalid.yml"), pytest.raises(ParserError)),
        (config_path("empty.yml"), pytest.raises(NameError)),
        (config_path("example.yml"), does_not_raise()),
    ],
)
def test_load_config_exception(filename, expected):
    with expected:
        args = parse_args(["-c", filename, "src"])
        load_config(args)


def test_load_config():
    args = parse_args(["-c", config_path("example.yml"), "src"])
    config = load_config(args)
    assert config["exclude"]["files"] == re.compile(r"\.npmrc|.*coded.*|\.git/.*")
    assert config["exclude"]["keys"] == re.compile("SECRET_VALUE_KEY")
    assert config["exclude"]["values"] == re.compile("SECRET_VALUE_PLACEHOLDER")


def test_default_config_structure():
    config = {"include": {}, "exclude": {}}
    default_config_structure(config)
    assert config["include"]["files"] == ["**/*"]
    assert config["exclude"]["files"] is None
    assert config["exclude"]["keys"] is None
    assert config["exclude"]["values"] is None
    assert config["rules"] == list_rule_ids(default_rules())
    assert config["severity"] == ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        ({"include": {}, "exclude": {}, "severity": ["BLOCKER"]}, ["BLOCKER"]),
        ({"include": {}, "exclude": {}}, ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]),
    ],
)
def test_default_config_structure_severity(config, expected):
    default_config_structure(config)
    assert config["severity"] == expected


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        ({"include": {}, "exclude": {}, "rules": ["rule-id"]}, ["rule-id"]),
        ({"include": {}, "exclude": {}}, list_rule_ids(default_rules())),
    ],
)
def test_default_config_structure_rules(config, expected):
    default_config_structure(config)
    assert config["rules"] == expected
