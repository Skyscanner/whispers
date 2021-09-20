import logging
from base64 import b64decode
from typing import Iterable, Iterator, Optional

from whispers.core.utils import (
    KeyValuePair,
    find_line_number,
    is_ascii,
    is_base64,
    is_base64_bytes,
    is_luhn,
    is_similar,
    is_uri,
)


def detect_secrets(rules: list, pairs: Iterable[KeyValuePair]) -> Iterator[KeyValuePair]:
    """Detect pairs with hardcoded secrets"""
    for pair in pairs:
        detected = filter(None, map(lambda rule: filter_rule(rule, pair), rules))
        tagged = map(tag_lineno, detected)

        yield from tagged


def tag_lineno(pair: KeyValuePair) -> KeyValuePair:
    """Add pair line number"""
    pair.line = find_line_number(pair)
    return pair


def filter_rule(rule: dict, pair: KeyValuePair) -> Optional[KeyValuePair]:
    """Filters based on rule"""
    if not filter_param("key", rule, pair):
        logging.debug(f"Rule '{rule['id']}' key '{pair.key}' failed")
        return None

    if not filter_param("value", rule, pair):
        logging.debug(f"Rule '{rule['id']}' value '{pair.value}' failed")
        return None

    if is_similar(pair.key, pair.value, rule["similar"]):
        logging.debug(f"Rule '{rule['id']}' pair '{pair.key}'/'{pair.value}' similar={rule['similar']} failed")
        return None

    pair.rule = {
        "id": rule["id"],
        "severity": rule["severity"],
        "message": rule["message"],
    }

    return pair


def filter_param(idx: str, rule: dict, pair: KeyValuePair) -> Optional[KeyValuePair]:
    """Filters based on key/value rule definition"""
    if idx not in rule:
        return pair

    isBase64 = rule[idx].get("isBase64", False)
    isAscii = rule[idx].get("isAscii", True)
    isUri = rule[idx].get("isUri", False)
    isLuhn = rule[idx].get("isLuhn", False)
    minlen = rule[idx].get("minlen", 0)
    regex = rule[idx].get("regex", None)

    target = pair.__dict__[idx]

    if isBase64:
        if is_base64(target) and isAscii:
            target = b64decode(target).decode("utf-8")
        elif is_base64_bytes(target) and not isAscii:
            target = b64decode(target)
        else:
            logging.debug(f"Target '{target}' isBase64={isBase64} failed")
            return None

    if isAscii != is_ascii(target):
        logging.debug(f"Target '{target}' isAscii={isAscii} failed")
        return None

    if isUri != is_uri(target):
        logging.debug(f"Target '{target}' isUri={isUri} failed")
        return None

    if isLuhn != is_luhn(target):
        logging.debug(f"Target '{target}' isLuhn={isLuhn} failed")
        return None

    target = pair.__dict__[idx]

    if minlen > len(target):
        logging.debug(f"Target '{target}' minlen={minlen} failed")
        return None

    if regex and not regex.match(target):
        logging.debug(f"Target '{target}' regex={regex} failed")
        return None

    return pair
