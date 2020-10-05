import re
from pathlib import Path
from typing import Optional

from whispers.plugins import WhisperPlugins
from whispers.rules import WhisperRules
from whispers.utils import Secret, simple_string, strip_string


class WhisperSecrets:
    def __init__(self, config):
        self.exclude = config["exclude"]
        self.breadcrumbs = []
        self.rules = WhisperRules()
        self.rules.load_rules_from_dict(config["rules"])

    def is_static(self, key: str, value: str) -> bool:
        """
        Check if given value is static (hardcoded).
        If value is dynamic, it's not a hardcoded secret.
        """
        if not isinstance(value, str):
            return False  # Not string
        if not value:
            return False  # Empty
        if value.startswith("$") and "$" not in value[2:]:
            return False  # Variable
        if "{{" in value and "}}" in value:
            return False  # Variable
        if value.startswith("{") and value.endswith("}"):
            if len(value) > 50:
                if self.rules.match("base64", value[1:-1]):
                    return True  # Token
            return False  # Variable
        if value.startswith("${") and value.endswith("}"):
            return False  # Variable
        if value.startswith("<") and value.endswith(">"):
            return False  # Placeholder
        if value == "null":
            return False  # IaC
        if re.match(r"\![A-Za-z]+ .+", value):
            return False  # IaC !Ref !Sub ...
        if self.rules.match("path", value):
            return False  # System path
        if key:
            s_key = simple_string(key)
            s_value = simple_string(value)
            if s_key == s_value:
                return False  # Placeholder
            if s_value.endswith(s_key):
                return False  # Placeholder
            for ex in self.exclude["keys"]:
                if ex.match(key):
                    return False  # Exclude keys
        for ex in self.exclude["values"]:
            if ex.match(value):
                return False  # Exclude values
        return True  # Hardcoded static value

    def is_excluded(self, breadcrumbs: list) -> bool:
        for crumb in breadcrumbs:
            for ex in self.exclude["keys"]:
                if ex.match(str(crumb)):
                    return True
        return False

    def detect_secrets(self, key: str, value: str, filepath: Path, breadcrumbs: list = []) -> Optional[Secret]:
        if not key:
            key = ""
        else:
            key = strip_string(key)
        if isinstance(value, str):
            value = strip_string(value)
        elif isinstance(value, int):
            value = str(value)
        else:
            return None  # Neither text nor digits
        if not self.is_static(key, value):
            return None  # Not static
        if self.is_excluded(breadcrumbs):
            return None  # Excluded via config
        return self.rules.check(key, value, filepath)

    def scan(self, filename: str) -> Optional[Secret]:
        plugin = WhisperPlugins(filename)
        if not plugin:
            return
        yield self.detect_secrets("file", plugin.filepath.as_posix(), plugin.filepath)
        for ret in plugin.pairs():
            if len(ret) == 2:  # key, value
                yield self.detect_secrets(ret[0], ret[1], plugin.filepath)
            elif len(ret) == 3:  # key, value, breadcrumbs
                yield self.detect_secrets(ret[0], ret[1], plugin.filepath, breadcrumbs=ret[2])
