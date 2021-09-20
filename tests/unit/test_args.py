from argparse import ArgumentParser
from io import StringIO, TextIOWrapper
from sys import stdout
from unittest.mock import patch

import pytest

from tests.unit.conftest import config_path, does_not_raise
from whispers.__version__ import __version__, __whispers__
from whispers.core.args import argument_parser, parse_args, show_info, show_splash


def test_argument_parser():
    assert isinstance(argument_parser(), ArgumentParser)


@pytest.mark.parametrize(
    ("arguments", "key", "expected", "exception"),
    [
        (["target"], "src", "target", does_not_raise()),
        (["target"], "output", stdout, does_not_raise()),
        (
            ["-c", config_path("detection_by_value.yml"), "src"],
            "config",
            config_path("detection_by_value.yml"),
            does_not_raise(),
        ),
        (["-r", "rule-1,rule-2", "src"], "rules", ["rule-1", "rule-2"], does_not_raise()),
        (["-e", "123", "src"], "exitcode", 123, does_not_raise()),
        (["-s", "a,b,c", "src"], "severity", ["a", "b", "c"], does_not_raise()),
        (["-i"], "info", True, pytest.raises(SystemExit)),
        (["-d"], "debug", True, pytest.raises(SystemExit)),
    ],
)
def test_parse_args(arguments, key, expected, exception):
    with exception:
        args = parse_args(arguments)
        assert args.__dict__[key] == expected


def test_parse_args_output():
    args = parse_args(["-o", "/tmp/out", "src"])
    assert isinstance(args.output, TextIOWrapper)


def test_show_info():
    mock_print = StringIO()
    with patch("sys.stdout", mock_print):
        show_info()
        result = mock_print.getvalue()
        assert "default rule IDs:" in result
        assert "default severity levels:" in result


def test_show_splash():
    mock_print = StringIO()
    with patch("sys.stdout", mock_print):
        show_splash(lambda: 1)()
        result = mock_print.getvalue()
        assert __version__ in result
        assert __whispers__ in result
