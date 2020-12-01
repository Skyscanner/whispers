from pathlib import Path
from re import compile

import pytest

from tests.unit.conftest import FIXTURE_PATH, does_not_raise, rule_path
from whispers.plugins import Yml
from whispers.rules import WhisperRules
from whispers.utils import load_yaml_from_file


@pytest.mark.parametrize(
    ("rulefile", "expectation"),
    [
        ("empty.yml", does_not_raise()),
        ("valid.yml", does_not_raise()),
        ("multiple.yml", does_not_raise()),
        ("invalid_severity.yml", pytest.raises(ValueError)),
    ],
)
def test_load_rules(rulefile, expectation):
    rules = WhisperRules(rulespath=rule_path("empty.yml"))
    rulefile = rule_path(rulefile)
    ruleyaml = load_yaml_from_file(Path(rulefile))
    with expectation:
        rules.load_rules(rulefile)
        assert len(rules.rules) == len(ruleyaml)
        for rule_id in ruleyaml.keys():
            assert rule_id in rules.rules


@pytest.mark.parametrize(
    ("rulefile", "expectation"),
    [("valid.yml", does_not_raise()), ("doesnotexist.yml", pytest.raises(FileNotFoundError))],
)
def test_load_rules_from_file(rulefile, expectation):
    rules = WhisperRules()
    rules_len = len(rules.rules)
    with expectation:
        rules.load_rules_from_file(Path(rule_path(rulefile)))
        assert len(rules.rules) == rules_len + 1


@pytest.mark.parametrize(
    ("rulefile", "rules_added"),
    [("empty.yml", 0), ("valid.yml", 1), ("multiple.yml", 4)],
)
def test_load_rules_from_dict(rulefile, rules_added):
    rules = WhisperRules()
    rules_len = len(rules.rules)
    custom_rules = load_yaml_from_file(Path(rule_path(rulefile)))
    rules.load_rules_from_dict(custom_rules)
    assert len(rules.rules) == rules_len + rules_added


@pytest.mark.parametrize(("dups", "expectation"), [(1, does_not_raise()), (2, pytest.raises(IndexError))])
def test_load_rule(dups, expectation):
    rules = WhisperRules()
    rulefile = Path(rule_path("valid.yml"))
    rule_id, rule = load_yaml_from_file(rulefile).popitem()
    with expectation:
        for _ in range(dups):
            rules.load_rule(rule_id, rule)
            assert rule_id in rules.rules
            assert rules.rules[rule_id] == rule


@pytest.mark.parametrize(
    ("rulefile", "expectation"),
    [("invalid_severity.yml", pytest.raises(ValueError)), ("multiple.yml", does_not_raise())],
)
def test_parse_rule(rulefile, expectation):
    rules = WhisperRules()
    rulefile = Path(rule_path(rulefile))
    rule_id, rule = load_yaml_from_file(rulefile).popitem()
    with expectation:
        parsed_rule = rules.parse_rule(rule_id, rule)
        for key in parsed_rule:
            assert parsed_rule[key] == rule[key]


@pytest.mark.parametrize(("value", "expectation"), [("test", True), ("Test", False), ("1test", False)])
def test_match(value, expectation):
    rules = WhisperRules(rulespath=rule_path("valid.yml"))
    assert rules.match("valid", value) == expectation


@pytest.mark.parametrize(
    ("ruleslist", "expectation"),
    [
        ("inexistent-rule-id", 0),
        ("apikey", 2),
        ("password", 3),
        ("apikey,password", 5),
    ],
)
def test_check(ruleslist, expectation):
    filepath = FIXTURE_PATH.joinpath("ruleslist.yml")
    rules = WhisperRules(ruleslist=ruleslist)
    result = 0
    for key, value, _ in Yml().pairs(filepath):
        if rules.check(key, value, filepath, []):
            result += 1
    assert result == expectation


@pytest.mark.parametrize(
    ("rule", "value", "expectation"),
    [
        ({"value": {"minlen": 1}}, "", False),
        ({"value": {"minlen": 1}}, "1", True),
        ({"key": {"minlen": 100}}, "whispers", True),
        ({"value": {"minlen": 4}}, "whispers", True),
        ({"value": {}}, "whispers", True),
        ({"value": {}}, b"binary", True),
        ({"value": {"minlen": -11}}, "", False),
        ({"value": {"minlen": None}}, "", False),
    ],
)
def test_check_minlen(rule, value, expectation):
    rules = WhisperRules()
    result = rules.check_minlen(rule, "value", value)
    assert result == expectation


@pytest.mark.parametrize(
    ("rule", "value", "expectation"),
    [
        ({"value": {"regex": compile(r"[a-z]+")}}, "whispers", True),
        ({"value": {"regex": compile(r"[A-Z]+")}}, "whispers", False),
        ({"key": {"regex": compile(r"[a-z]+")}}, "whispers", True),
        ({"value": {"regex": compile(r"[a-z]+")}}, b"binary", False),
        ({"value": {"regex": compile(r"[a-z]+")}}, 1, False),
        ({"value": {"regex": compile(r"[a-z]+")}}, None, False),
    ],
)
def test_check_regex(rule, value, expectation):
    rules = WhisperRules()
    result = rules.check_regex(rule, "value", value)
    assert result == expectation


@pytest.mark.parametrize(
    ("rule", "key", "value", "expectation"),
    [
        ({"similar": 0.3}, "A", "a", True),
        ({"similar": 0.3}, "B", "a", False),
        ({"similar": 0.3}, "a", "a" * 5, True),
        ({"similar": 0.3}, "a", "a" * 6, False),
        ({"similar": 0.3}, "API_TOKEN", "${API_TOKEN}", True),
        ({"similar": 0.3}, "API_TOKEN", "API_TOKEN_PLACEHOLDER", True),
    ],
)
def test_check_similar(rule, key, value, expectation):
    rules = WhisperRules()
    result = rules.check_similar(rule, key, value)
    assert result == expectation


@pytest.mark.parametrize(
    ("test", "value", "expectation"),
    [
        (True, "d2hpc3BlcnM=", "whispers"),
        (False, "d2hpc3BlcnM=", "d2hpc3BlcnM="),
        (False, "whisper$", "whisper$"),
        (False, None, None),
        (False, 1, 1),
    ],
)
def test_decode_if_base64(test, value, expectation):
    rules = WhisperRules()
    rule = {"isBase64": test}
    result = rules.decode_if_base64(rule, value)
    assert result == expectation


@pytest.mark.parametrize(
    ("value", "expectation"),
    [("whispers", True), (123, False), (b"binary", False), (None, False), ("шёпот", False)],
)
def test_is_ascii(value, expectation):
    rules = WhisperRules()
    result = rules.is_ascii(value)
    assert result == expectation
