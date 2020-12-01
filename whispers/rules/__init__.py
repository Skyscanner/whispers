import re
from base64 import b64decode
from pathlib import Path
from typing import List

from luhn import verify as luhn_verify

from whispers.utils import Secret, find_line_number, load_yaml_from_file, similar_strings


class WhisperRules:
    def __init__(self, ruleslist: str = "all", rulespath: str = ""):
        """
        Loads rules

        @ruleslist: comma-separated list of rule IDs
        @rulespath: file or directory with rules.yml
        """
        self.rules = {}
        self.ruleslist = ruleslist.split(",")
        self.load_rules(rulespath)

    def load_rules(self, rulespath: str = ""):
        if not rulespath:
            rulespath = Path(__file__).parent
        else:
            rulespath = Path(rulespath)
        if rulespath.is_dir():
            for rulefile in rulespath.glob("*.yml"):
                self.load_rules_from_file(rulefile)
        elif rulespath.is_file():
            self.load_rules_from_file(rulespath)
        else:
            raise TypeError("Rules must be loaded from a file or directory")

    def load_rules_from_file(self, rulefile: Path):
        if not rulefile.exists():
            raise FileNotFoundError(f"Rule file {rulefile.as_posix()} not found")
        rules = load_yaml_from_file(rulefile)
        for rule_id, rule in rules.items():
            self.load_rule(rule_id, rule)

    def load_rules_from_dict(self, custom_rules: dict):
        if not custom_rules:
            return
        for rule_id, rule in custom_rules.items():
            self.load_rule(rule_id, rule)

    def load_rule(self, rule_id: str, rule: dict):
        if rule_id in self.rules:
            raise IndexError(f"Duplicated rule {rule_id}, {self.rules[rule_id]}")
        self.rules[rule_id] = self.parse_rule(rule_id, rule)

    @staticmethod
    def parse_rule(rule_id: str, rule: dict) -> dict:
        required_severity = ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]
        if rule["severity"] not in required_severity:
            raise ValueError(f"Missing severity specification in rule {rule_id}")
        for idx in ("key", "value"):
            if idx not in rule:
                continue
            if "regex" not in rule[idx]:
                continue
            flags = 0
            if rule[idx]["ignorecase"]:
                flags = re.IGNORECASE
            rule[idx]["regex"] = re.compile(rule[idx]["regex"], flags=flags)
        return rule

    def match(self, rule_id: str, text: str):
        for idx in ("key", "value"):
            if idx in self.rules[rule_id]:
                regex = self.rules[rule_id][idx]["regex"]
                if regex.match(text):
                    return True
        return False

    def check(self, key: str, value: str, filepath: Path, foundlines: List[int]) -> Secret:
        matrix = {"key": key, "value": value}
        checks = {
            "minlen": self.check_minlen,
            "regex": self.check_regex,
            "isBase64": self.check_isBase64,
            "isAscii": self.check_isAscii,
            "isUri": self.check_isUri,
            "isLuhn": self.check_isLuhn,
        }
        for rule_id, rule in self.rules.items():
            rule_matched = True
            if self.ruleslist != ["all"]:
                if rule_id not in self.ruleslist:
                    continue  # Only report configured rules
            else:
                if rule["severity"] == "INFO":
                    continue  # Don't report INFO on all rules
            if "similar" in rule:
                if self.check_similar(rule, key, value):
                    rule_matched = False
            for check_idx, check_function in checks.items():
                if not rule_matched:
                    break
                for mkey, mvalue in matrix.items():
                    if mkey not in rule:
                        continue
                    if check_idx not in rule[mkey]:
                        continue
                    if not check_function(rule, mkey, mvalue):
                        rule_matched = False
                        break
            if not rule_matched:
                continue
            return Secret(
                filepath.as_posix(),
                find_line_number(filepath, key, value, foundlines),
                key,
                value,
                self.rules[rule_id]["message"],
                self.rules[rule_id]["severity"],
            )

    def check_isBase64(self, rule, mkey, mvalue):
        return rule[mkey]["isBase64"] == self.match("base64", mvalue)

    def check_isAscii(self, rule, mkey, mvalue):
        mvalue = self.decode_if_base64(mkey, mvalue)
        return self.is_ascii(mvalue)

    def check_isUri(self, rule, mkey, mvalue):
        mvalue = self.decode_if_base64(mkey, mvalue)
        return rule[mkey]["isUri"] == self.match("uri", mvalue)

    @staticmethod
    def check_minlen(rule, mkey, mvalue):
        if mkey not in rule:
            return True  # Not specified
        if "minlen" not in rule[mkey]:
            return True  # Not specified
        minlen = rule[mkey]["minlen"]
        if not isinstance(minlen, int):
            return False  # Not numeric
        if minlen < 0:
            return False  # Negative length
        return len(mvalue) >= minlen

    @staticmethod
    def check_regex(rule, mkey, mvalue):
        if mkey not in rule:
            return True  # Not specified
        if "regex" not in rule[mkey]:
            return True  # Not specified
        if not isinstance(mvalue, str):
            return False  # Not text
        if not rule[mkey]["regex"].match(mvalue):
            return False  # No match
        return True  # Match

    @staticmethod
    def check_similar(rule, key, value):
        """
        Checks similarity between key and value.
        Default rule similarity is 0.3
        Returns True if actual similarity is
        greater than the rule similarity.
        """
        if "similar" not in rule:
            return similar_strings(key, value) >= 0.3
        similar = rule["similar"]
        if not isinstance(similar, float):
            return False  # Not float
        return similar_strings(key, value) >= similar

    @staticmethod
    def check_isLuhn(rule, key, value):
        if not value.isnumeric():
            return False
        return luhn_verify(value)

    @staticmethod
    def decode_if_base64(mkey, mvalue):
        if "isBase64" in mkey:
            if mkey["isBase64"]:
                mvalue = b64decode(mvalue).decode("utf-8")
        return mvalue

    @staticmethod
    def is_ascii(data):
        if not isinstance(data, str):
            return False
        for ch in data:
            if ord(ch) not in range(32, 127):
                return False
        return True
