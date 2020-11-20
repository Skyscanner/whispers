import json
import re
from collections import namedtuple
from hashlib import md5
from pathlib import Path
from typing import List, Optional

from Levenshtein import ratio
from yaml import safe_load

Secret = namedtuple("Secret", ["file", "line", "key", "value", "message", "severity"])


escaped_chars = str.maketrans({"'": r"\'", '"': r"\""})


def strip_string(value: str) -> str:
    """
    Strips leading and trailing quotes and spaces
    """
    if not value:
        return ""
    return str(value).strip(" '\"\n\r\t")


def simple_string(value: str) -> str:
    """
    Returns a simplified value for loose comparison
    """
    if not value:
        return ""
    value = strip_string(value)  # Remove quotes
    value = value.rstrip("\\")  # Remove trailing backslashes
    value = value.lower()  # Lowercase
    value = re.sub(r"[^a-z0-9]", "_", value.strip())  # Simplify
    return value


def similar_strings(a: str, b: str) -> float:
    """
    Returns similarity coefficient between two strings
    """
    a = simple_string(a).replace("_", "")
    b = simple_string(b).replace("_", "")
    return ratio(a, b)


def string_is_quoted(value: str) -> bool:
    """
    Checks if the value is between single or double quotes
    """
    quotes = ('"', "'")
    return value.startswith(quotes) and value.endswith(quotes)


def string_is_function(value: str) -> bool:
    """
    Checks if the value resembles a function call
    """
    open_brackets = value.count("(")
    close_brackets = value.count(")")
    if open_brackets:
        return open_brackets == close_brackets
    return False


def line_with_key_value(key: str, value: str, line: str) -> bool:
    """
    Both key and value are on the same line
    """
    return key in line and value in line


def line_with_value(value: str, line: str) -> bool:
    """
    Line containing just the value
    """
    return value in line


def line_begins_with_value(value: str, line: str) -> bool:
    """
    Find the line where the value begins
    """
    value_str = simple_string(value)
    line_str = simple_string(line)
    return value_str.startswith(line_str)


def find_line_number(filepath: Path, key: str, value: str, foundlines: List[int]) -> int:
    """
    Returns line number in file with given key and value
    """
    if not value:
        return 0
    value = value.split("\n")[0]
    value_line_number = 0
    for line_number, line in enumerate(filepath.open().readlines(), 1):
        if not strip_string(line):
            continue
        if line_number in foundlines:
            continue
        if line_with_key_value(key, value, line):
            foundlines.append(line_number)
            return line_number
        elif line_begins_with_value(value, line):
            foundlines.append(line_number)
            return line_number
        elif line_with_value(value, line):
            value_line_number = line_number
    if value_line_number:
        foundlines.append(value_line_number)
    return value_line_number


def load_yaml_from_file(filepath: Path) -> dict:
    ret = safe_load(filepath.read_text())
    if not isinstance(ret, dict):
        return {}
    return ret


def secret_checksum(secret: Secret) -> str:
    secret = json.dumps(secret._asdict())
    chk = md5()
    chk.update(secret.encode("utf-8"))
    return chk.hexdigest()


def format_secret(secret: Secret) -> str:
    return (
        secret_checksum(secret)
        + ":\n"
        + '  file: "'
        + str(secret.file)
        + '"\n'
        + '  line: "'
        + str(secret.line)
        + '"\n'
        + '  key: "'
        + str(secret.key)
        + '"\n'
        + '  value: "'
        + str(secret.value)
        + '"\n'
        + '  message: "'
        + str(secret.message)
        + '"\n'
        + '  severity: "'
        + str(secret.severity)
        + '"\n'
        + "\n"
    )


def format_stdout(secret: Secret, output: Optional[Path] = None) -> str:
    if output:
        output.open("a").write(format_secret(secret))
    data = json.dumps(secret._asdict())
    print(data)
    return data
