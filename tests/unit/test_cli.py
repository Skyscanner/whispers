from argparse import ArgumentParser
from io import StringIO
from unittest.mock import patch

import pytest

from tests.unit.conftest import config_path, does_not_raise, fixture_path
from whispers.cli import cli, cli_info, cli_parser, parse_args
from whispers.rules import WhisperRules


def test_cli_parser():
    assert isinstance(cli_parser(), ArgumentParser)


@pytest.mark.parametrize(
    ("arguments", "expectation"),
    [
        ([], {"config": None, "output": None, "rules": "all", "src": None}),
        (["whispers.json"], {"config": None, "output": None, "rules": "all", "src": "whispers.json"}),
        (["-c", "whispers.yml"], {"config": "whispers.yml", "output": None, "rules": "all", "src": None}),
        (["-r", "whis,pers"], {"config": None, "output": None, "rules": "whis,pers", "src": None}),
        (["-o", "/tmp/whispers"], {"config": None, "output": "/tmp/whispers", "rules": "all", "src": None}),
    ],
)
def test_parse_args(arguments, expectation):
    args = parse_args(arguments)
    assert args.config == expectation["config"]
    assert args.output == expectation["output"]
    assert args.rules == expectation["rules"]
    assert args.src == expectation["src"]


@pytest.mark.parametrize(
    ("arguments", "expectation"),
    [
        ([], pytest.raises(SystemExit)),
        (["-v"], pytest.raises(SystemExit)),
        (["-i"], pytest.raises(SystemExit)),
        (["-c", "whispers.yml"], pytest.raises(SystemExit)),
        (["-r", "whis,pers"], pytest.raises(SystemExit)),
        (["-o", "/tmp/whispers"], pytest.raises(SystemExit)),
        (["/dev/null/bin"], pytest.raises(FileNotFoundError)),
        ([fixture_path("hardcoded.json")], does_not_raise()),
        ([fixture_path("hardcoded.json"), "-o", "/tmp/whispers"], does_not_raise()),
        ([fixture_path("hardcoded.json"), "-c", config_path("example.yml")], does_not_raise()),
    ],
)
def test_cli(arguments, expectation):
    with expectation:
        assert cli(arguments) is None


def test_cli_info():
    mock_print = StringIO()
    with patch("sys.stdout", mock_print):
        cli_info()
        result = mock_print.getvalue()
        assert "available rules" in result
        for rule_id in WhisperRules().rules.keys():
            assert rule_id in result
