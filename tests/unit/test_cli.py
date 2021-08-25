import os
import re
import shlex
import subprocess
from argparse import ArgumentParser
from io import StringIO
from pathlib import Path
from tempfile import mkstemp
from unittest.mock import patch

import pytest

from tests.unit.conftest import config_path, does_not_raise
from whispers.cli import cli, cli_info, cli_parser, parse_args
from whispers.rules import WhisperRules
from whispers.utils import load_yaml_from_file


def test_cli_parser():
    assert isinstance(cli_parser(), ArgumentParser)


@pytest.mark.parametrize(
    ("arguments", "expected", "result"),
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
        (["-e", "123", "src"], does_not_raise(), {"exitcode": 123}),
        (["-s", "a,b,c", "src"], does_not_raise(), {"severity": ["a", "b", "c"]}),
    ],
)
def test_parse_args(arguments, expected, result):
    with expected:
        args = parse_args(arguments)
        for key, value in result.items():
            assert args.__dict__[key] == value


def test_cli():
    sysexit = pytest.raises(SystemExit)
    with sysexit:
        assert cli() == 0
        assert sysexit.code == 0


def test_cli_info():
    mock_print = StringIO()
    with patch("sys.stdout", mock_print):
        cli_info()
        result = mock_print.getvalue()
        assert "available rule IDs" in result
        for rule_id in WhisperRules().rules.keys():
            assert rule_id in result


@pytest.mark.parametrize(("arg", "expected"), [("", 0), ("-e 123", 123)])
def test_cli_exitcode(arg, expected):
    proc = subprocess.Popen(
        shlex.split(f"whispers {arg} -r apikey tests/fixtures/apikeys.yml"), stdout=subprocess.DEVNULL
    )
    proc.communicate()
    assert proc.returncode == expected


@pytest.mark.parametrize(
    ("arg", "expected"),
    [
        ("", ["BLOCKER", "CRITICAL", "MAJOR", "MINOR"]),
        ("-s BLOCKER", ["BLOCKER"]),
        ("-s CRITICAL,MINOR", ["CRITICAL", "MINOR"]),
    ],
)
def test_cli_severity(arg, expected):
    fd, tmp = mkstemp(suffix=".yml", text=True)
    proc = subprocess.Popen(
        shlex.split(
            f"whispers -o {tmp} {arg} -r aws-id,privatekey,apikey,slack-webhook,base64 tests/fixtures/severity.yml"
        ),
        stdout=subprocess.DEVNULL,
    )
    proc.communicate()
    result = load_yaml_from_file(Path(tmp))
    os.close(fd)
    os.remove(tmp)
    assert len(result) == len(expected)
    for value in result.values():
        assert value["severity"] in expected
