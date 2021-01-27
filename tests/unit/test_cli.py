import re
from argparse import ArgumentParser
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.unit.conftest import config_path, does_not_raise
from whispers.cli import cli, cli_info, cli_parser, parse_args
from whispers.rules import WhisperRules


def test_cli_parser():
    assert isinstance(cli_parser(), ArgumentParser)


@pytest.mark.parametrize(
    ("arguments", "expectation", "result"),
    [
        ([], pytest.raises(SystemExit), None),
        (["src"], does_not_raise(), {"config": None, "output": None, "rules": "all", "src": "src"}),
        (
            ["-c", config_path("detection_by_value.yml"), "src"],
            does_not_raise(),
            {
                "config": {
                    "exclude": {"keys": [re.compile("^file$", re.IGNORECASE)], "files": [], "values": []},
                    "include": {"files": ["**/*"]},
                    "rules": {},
                },
                "src": "src",
            },
        ),
        (["-r", "rule-1,rule-2", "src"], does_not_raise(), {"rules": "rule-1,rule-2"}),
        (["-o", "/tmp/output", "src"], does_not_raise(), {"output": Path("/tmp/output")}),
    ],
)
def test_parse_args(arguments, expectation, result):
    with expectation:
        args = parse_args(arguments)
        for key, value in result.items():
            assert args.__dict__[key] == value


@pytest.mark.parametrize(
    ("expectation"),
    [
        (pytest.raises(SystemExit)),
    ],
)
def test_cli(expectation):
    with expectation:
        assert cli() is None


def test_cli_info():
    mock_print = StringIO()
    with patch("sys.stdout", mock_print):
        cli_info()
        result = mock_print.getvalue()
        assert "available rules" in result
        for rule_id in WhisperRules().rules.keys():
            assert rule_id in result
