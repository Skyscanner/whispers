import re
from pathlib import Path

import pytest

from tests.unit.conftest import FIXTURE_PATH, fixture_path
from whispers.core.args import parse_args
from whispers.core.config import load_config
from whispers.core.pairs import filter_included, filter_static, is_static, load_plugin, make_pairs, tag_file
from whispers.core.utils import KeyValuePair
from whispers.plugins.config import Config
from whispers.plugins.dockercfg import Dockercfg
from whispers.plugins.dockerfile import Dockerfile
from whispers.plugins.html import Html
from whispers.plugins.htpasswd import Htpasswd
from whispers.plugins.jproperties import Jproperties
from whispers.plugins.json import Json
from whispers.plugins.npmrc import Npmrc
from whispers.plugins.pip import Pip
from whispers.plugins.plaintext import Plaintext
from whispers.plugins.pypirc import Pypirc
from whispers.plugins.python import Python
from whispers.plugins.shell import Shell
from whispers.plugins.xml import Xml
from whispers.plugins.yml import Yml


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("File.404", 0),
        ("/tmp", 0),
        (fixture_path("language.py2"), 1),
        (fixture_path(".npmrc"), 4),
        (fixture_path("placeholders.xml"), 1),
    ],
)
def test_make_pairs(filename, expected):
    args = parse_args([filename])
    config = load_config(args)
    pairs = list(make_pairs(config, Path(filename)))
    assert len(pairs) == expected


def test_tag_file():
    pair = KeyValuePair("key", "value", file="")
    assert tag_file(FIXTURE_PATH, pair).file == fixture_path()


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("is", "included", KeyValuePair("is", "included", ["is"])),
        ("is_not", "included", None),
        ("is", "excluded", None),
    ],
)
def test_filter_included(key, value, expected):
    args = parse_args([fixture_path()])
    config = load_config(args)
    config["exclude"]["keys"] = re.compile(r"is_not")
    config["exclude"]["values"] = re.compile(r"excluded")
    pair = KeyValuePair(key, value, [key])
    assert filter_included(config, pair) == expected


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("aws_secret", "${aws_secret}", None),
        ("thesame", "THESAME", None),
        ("is", "static", KeyValuePair("is", "static")),
    ],
)
def test_filter_static(key, value, expected):
    pair = KeyValuePair(key, value)
    assert filter_static(pair) == expected


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        (None, None, False),
        ("key", "", False),
        ("key", "$value", False),
        ("key", "{{value}}", False),
        ("key", "{value}", False),
        ("key", "{whispers~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~}", False),
        ("key", "{d2hpc3BlcnN+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+}", True),
        ("key", "${value$}", False),
        ("key", "<value>", False),
        ("key", "{value}", False),
        ("key", "null", False),
        ("key", "!Ref Value", False),
        ("key", "{value}", False),
        ("key", "/system/path/value", False),
        ("thesame", "THESAME", False),
        ("label", "WhispersLabel", False),
        ("_key", "-key", False),
        ("_secret_value_placeholder_", "----SECRET-VALUE-PLACEHOLDER-", False),
        ("_secret_value_placeholder_", "----SECRET-VALUE-PLACEHOLDER--", True),
        ("SECRET_VALUE_KEY", "whispers", True),
        ("whispers", "SECRET_VALUE_PLACEHOLDER", True),
        ("secret", "whispers", True),
    ],
)
def test_is_static(key, value, expected):
    assert is_static(key, value) == expected


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("File.404", None),
        ("", None),
        (".htpasswd", Htpasswd),
        (".npmrc", Npmrc),
        (".pypirc", Pypirc),
        ("apikeys.json", Json),
        ("invalid.json", Json),
        ("apikeys.yml", Yml),
        ("cloudformation.yml", Yml),
        ("passwords.yml", Yml),
        ("beans.xml", Xml),
        ("beans.xml.dist", Xml),
        ("beans.xml.template", Xml),
        ("apikeys.xml", Xml),
        ("connection.config", Xml),
        ("integration.conf", Xml),
        ("Dockerfile", Dockerfile),
        (".dockercfg", Dockercfg),
        ("java.properties", Jproperties),
        ("pip.conf", Pip),
        ("plaintext.txt", Plaintext),
        (".aws/credentials", Config),
        ("settings.cfg", Config),
        ("settings.env", Config),
        ("settings.ini", Config),
        ("language.sh", Shell),
        ("language.py", Python),
        ("cors.py", Python),
        ("language.html", Html),
    ],
)
def test_load_plugin(filename, expected):
    plugin = load_plugin(FIXTURE_PATH.joinpath(filename))
    assert plugin == expected
