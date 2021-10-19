import logging
import re
from argparse import Namespace
from typing import List

from yaml import safe_load_all

from whispers.core.utils import DEFAULT_PATH


def load_rules(args: Namespace, config: dict) -> List[dict]:
    """Loads applicable rules based on args and config"""
    rule_ids = args.rules or config["rules"]
    severities = args.severity or config["severity"]
    applicable_rules = []

    # Load from default rules based on rules/severity config
    for rule in default_rules():
        rule_id = rule["id"].strip()
        rule_severity = rule["severity"].strip()

        if rule_id not in rule_ids:
            continue

        if rule_severity not in severities:
            continue

        default_rule_structure(rule)
        applicable_rules.append(rule)

    # Load inline rules from config file (if any)
    for rule in rule_ids:
        if isinstance(rule, str):
            continue

        default_rule_structure(rule)
        applicable_rules.append(rule)

    logging.debug(f"Loaded {len(applicable_rules)} rules '{applicable_rules}'")
    return applicable_rules


def default_rule_structure(rule: dict):
    """Ensure minimal expected rule structure"""
    required = ["id", "message", "severity"]
    list(map(lambda key: _ensure_exists(key, rule), required))

    for param in ["key", "value"]:
        if param not in rule:
            continue

        if "regex" not in rule[param]:
            continue

        ignorecase = rule[param].get("ignorecase", False)
        flags = re.IGNORECASE if ignorecase else 0
        rule[param]["regex"] = re.compile(rule[param]["regex"], flags=flags)

    if "similar" not in rule:
        rule["similar"] = 1

    if "description" in rule:
        del rule["description"]


def _ensure_exists(key: str, rule: dict):
    """Ensure both rule key and its value are defined"""
    if key not in rule or not rule[key]:
        raise IndexError(f"Rule '{rule}' is missing '{key}' specification")


def default_rules() -> List[dict]:
    """Read and parse builtin rules"""
    rules = []
    files = DEFAULT_PATH.joinpath("rules").glob("*.yml")
    for file in files:
        list(map(rules.extend, safe_load_all(file.read_text())))

    return rules


def list_rule_ids(rules: List[dict]) -> List[str]:
    """List rule IDs given a list of rules"""
    ids = sorted(map(lambda rule: rule["id"], rules))

    return ids
