import pytest

from tests.unit.conftest import FIXTURE_PATH, config_path, fixture_path
from whispers.core.args import parse_args
from whispers.core.config import load_config
from whispers.core.pairs import make_pairs
from whispers.core.rules import default_rule_structure, load_rules
from whispers.core.secrets import detect_secrets, filter_param, filter_rule, tag_lineno
from whispers.core.utils import KeyValuePair, is_base64


@pytest.fixture
def rule_fixture():
    return {"id": "fixture", "message": "test", "severity": "INFO", "key": {}, "value": {}}


@pytest.mark.parametrize(("idx", "expected"), [("key", KeyValuePair), ("value", type(None)),])
def test_filter_param_by_idx(idx, expected, rule_fixture):
    pair = KeyValuePair("sonar.jdbc.password", "a")
    rule_fixture["key"] = {"regex": r"sonar.jdbc.password", "ignorecase": False}
    rule_fixture["value"] = {"minlen": 2}
    default_rule_structure(rule_fixture)

    result = filter_param(idx, rule_fixture, pair)

    assert isinstance(result, expected)


@pytest.mark.parametrize(
    ("value", "isBase64", "isAscii", "isUri", "isLuhn", "expected"),
    [
        ("test", True, True, True, True, type(None)),
        ("test", True, True, True, False, type(None)),
        ("test", True, True, False, True, type(None)),
        ("dGVzdAo=", True, True, False, False, KeyValuePair),
        ("test", True, False, True, True, type(None)),
        ("test", True, False, True, False, type(None)),
        ("test", True, False, False, True, type(None)),
        (b"test", True, False, False, False, KeyValuePair),
        ("test", False, True, True, True, type(None)),
        ("http://localhost.localdomain", False, True, True, False, KeyValuePair),
        ("4111111111111111", False, True, False, True, KeyValuePair),
        ("test", False, True, False, False, KeyValuePair),
        ("test", False, False, True, True, type(None)),
        ("http://localhost.localdomain", False, False, True, False, type(None)),
        (b"4111111111111111", False, False, False, True, type(None)),
        (b"test", False, False, False, False, type(None)),
    ],
)
def test_filter_param_by_rule_flags(value, isBase64, isAscii, isUri, isLuhn, expected, rule_fixture):
    pair = KeyValuePair("key", value)
    rule_fixture["value"] = {
        "isBase64": isBase64,
        "isAscii": isAscii,
        "isUri": isUri,
        "isLuhn": isLuhn,
    }
    default_rule_structure(rule_fixture)

    result = filter_param("value", rule_fixture, pair)

    assert isinstance(result, expected)


@pytest.mark.parametrize(("minlen", "expected"), [(0, KeyValuePair), (4, KeyValuePair), (5, type(None)),])
def test_filter_param_by_rule_minlen(minlen, expected, rule_fixture):
    pair = KeyValuePair("key", "test")
    rule_fixture["value"] = {"minlen": minlen}
    default_rule_structure(rule_fixture)

    result = filter_param("value", rule_fixture, pair)

    assert isinstance(result, expected)


@pytest.mark.parametrize(
    ("key", "value", "similar", "expected"),
    [
        ("key", "KEY", 1, type(None)),
        ("key", "KEY", 0, type(None)),
        ("key", "value", 0.3, KeyValuePair),
        ("key", "value", 0, type(None)),
    ],
)
def test_filter_rule_similar(key, value, similar, expected, rule_fixture):
    pair = KeyValuePair(key, value)
    rule_fixture["similar"] = similar
    default_rule_structure(rule_fixture)

    result = filter_rule(rule_fixture, pair)

    assert isinstance(result, expected)


@pytest.mark.parametrize(
    ("regex", "ignorecase", "expected"),
    [(r"tes.*", True, KeyValuePair), (r"Tes.*", False, type(None)), (r"a.*", True, type(None)),],
)
def test_filter_param_by_rule_regex(regex, ignorecase, expected, rule_fixture):
    pair = KeyValuePair("key", "test")
    rule_fixture["value"] = {"regex": regex, "ignorecase": ignorecase}
    default_rule_structure(rule_fixture)

    result = filter_param("value", rule_fixture, pair)

    assert isinstance(result, expected)


def test_tag_lineno():
    pair = KeyValuePair("sonar.jdbc.password", "hardcoded02", file=FIXTURE_PATH.joinpath("java.properties"))

    assert tag_lineno(pair).line == 10


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        ("privatekeys.yml", ["access", "key", "rsa", "dsa", "ec", "openssh"]),
        ("privatekeys.json", ["access", "key", "rsa", "dsa", "ec", "openssh"]),
        ("privatekeys.xml", ["access", "key", "rsa", "dsa", "ec", "openssh"]),
        ("aws.yml", ["aws_id", "aws_key", "aws_token"]),
        ("aws.json", ["aws_id", "aws_key", "aws_token"]),
        ("aws.xml", ["aws_id", "aws_key", "aws_token"]),
        ("jenkins.xml", ["noncompliantApiToken", "noncompliantPasswordHash"]),
        ("cloudformation.yml", ["NoncompliantDBPassword"]),
        ("cloudformation.json", ["NoncompliantDBPassword"]),
    ],
)
def test_detect_secrets_by_key(src, expected):
    args = parse_args([fixture_path(src)])
    config = load_config(args)
    rules = load_rules(args, config)
    pairs = make_pairs(config, FIXTURE_PATH.joinpath(src))
    result = list(map(lambda x: x.key, detect_secrets(rules, pairs)))
    assert set(result) == set(expected)


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        (".aws/credentials", 5),
        (".dockercfg", 1),
        (".htpasswd", 2),
        (".npmrc", 3),
        (".pypirc", 1),
        ("Dockerfile", 3),
        ("apikeys.json", 10),
        ("apikeys.xml", 10),
        ("apikeys.yml", 10),
        ("beans.xml", 3),
        ("beans.xml.dist", 3),
        ("beans.xml.template", 3),
        ("creditcards.yml", 3),
        ("cloudformation.json", 1),
        ("cloudformation.json.template", 0),
        ("custom.json", 0),
        ("custom.xml", 0),
        ("custom.yml", 0),
        ("empty.dockercfg", 0),
        ("falsepositive.yml", 4),
        ("gitkeys.yml", 5),
        ("hardcoded.json", 5),
        ("hardcoded.xml", 5),
        ("hardcoded.yml", 5),
        ("integration.conf", 5),
        ("integration.json", 5),
        ("integration.xml", 5),
        ("integration.yml", 5),
        ("invalid.yml", 0),
        ("invalid.json", 0),
        ("java.properties", 3),
        ("jdbc.xml", 3),
        ("language.html", 3),
        ("language.py", 11),
        ("language.py2", 0),
        ("language.sh", 14),
        ("passwords.json", 5),
        ("passwords.xml", 5),
        ("passwords.yml", 5),
        ("pip.conf", 2),
        ("placeholders.json", 0),
        ("placeholders.xml", 0),
        ("placeholders.yml", 0),
        ("plaintext.txt", 2),
        ("settings.cfg", 1),
        ("settings.conf", 1),
        ("settings.env", 1),
        ("settings.ini", 1),
        ("uri.yml", 2),
        ("webhooks.yml", 3),
    ],
)
def test_detect_secrets_by_value(src, expected):
    args = parse_args(["-c", config_path("detection_by_value.yml"), fixture_path(src)])
    config = load_config(args)
    rules = load_rules(args, config)
    pairs = make_pairs(config, FIXTURE_PATH.joinpath(src))
    result = list(map(lambda x: x.value, detect_secrets(rules, pairs)))
    assert len(result) == expected
    for value in result:
        if value.isnumeric() or is_base64(value):
            continue

        assert "hardcoded" in value.lower()


@pytest.mark.parametrize(
    ("expected"),
    [
        (".aws/credentials"),
        (".htpasswd"),
        (".npmrc"),
        (".pypirc"),
        ("connection.config"),
        ("integration.conf"),
        ("pip.conf"),
        ("settings.cfg"),
        ("settings.conf"),
        ("settings.env"),
        ("settings.ini"),
    ],
)
def test_detect_secrets_by_filename(expected):
    args = parse_args(["-c", config_path("detection_by_filename.yml"), fixture_path(expected)])
    config = load_config(args)
    rules = load_rules(args, config)
    pairs = make_pairs(config, FIXTURE_PATH.joinpath(expected))
    result = map(lambda x: x.file, detect_secrets(rules, pairs))
    for item in result:
        assert item.endswith(expected)


@pytest.mark.parametrize(
    ("src", "count", "rule_id"), [("language.html", 3, "comments"), ("passwords.json", 5, "password"),],
)
def test_detect_secrets_by_rule(src, count, rule_id):
    args = parse_args(["-r", rule_id, "-c", config_path("detection_by_value.yml"), fixture_path(src)])
    config = load_config(args)
    rules = load_rules(args, config)
    pairs = make_pairs(config, FIXTURE_PATH.joinpath(src))
    result = list(map(lambda x: x.rule["id"], detect_secrets(rules, pairs)))
    assert len(result) == count
    for item in result:
        assert item == rule_id
