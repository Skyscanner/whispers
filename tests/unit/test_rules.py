from pathlib import Path

import pytest

from whispers.rules import WhisperRules
from whispers.utils import load_yaml_from_file

from .conftest import does_not_raise, rule_path


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
    rules = WhisperRules(rule_path("empty.yml"))
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
    [("invalid_severity.yml", pytest.raises(ValueError))],
)
def test_parse_rule(rulefile, expectation):
    rules = WhisperRules()
    rulefile = Path(rule_path(rulefile))
    rule_id, rule = load_yaml_from_file(rulefile).popitem()
    with expectation:
        parsed_rule = rules.parse_rule(rule_id, rule)
        assert parsed_rule["message"] == rule["message"]
        # TODO: add the rest of asserts


@pytest.mark.parametrize(("value", "result"), [("test", True), ("Test", False), ("1test", False)])
def test_match(value, result):
    rules = WhisperRules(rule_path("valid.yml"))
    assert rules.match("valid", value) == result
