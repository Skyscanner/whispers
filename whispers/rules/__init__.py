import re
from base64 import b64decode
from pathlib import Path

from whispers.utils import Secret, find_line_number, load_yaml_from_file, similar_strings


class WhisperRules:
    def __init__(self, rulespath: str = ""):
        self.rules = {}
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

    def check(self, key, value, filepath):
        def decode_if_base64(mkey, mvalue):
            if "isBase64" in mkey:
                if mkey["isBase64"]:
                    mvalue = b64decode(mvalue)
            return mvalue

        def is_ascii(data):
            if not isinstance(data, str):
                return False
            for ch in data:
                if ord(ch) not in range(32, 127):
                    return False
            return True

        def check_minlen(rule, mkey, mvalue):
            return len(mvalue) >= int(rule[mkey]["minlen"])

        def check_regex(rule, mkey, mvalue):
            return rule[mkey]["regex"].match(mvalue)

        def check_isBase64(rule, mkey, mvalue):
            return rule[mkey]["isBase64"] == self.match("base64", mvalue)

        def check_isAscii(rule, mkey, mvalue):
            mvalue = decode_if_base64(mkey, mvalue)
            return is_ascii(mvalue)

        def check_isUri(rule, mkey, mvalue):
            mvalue = decode_if_base64(mkey, mvalue)
            return rule[mkey]["isUri"] == self.match("uri", mvalue)

        def check_similar(rule, key, value):
            return similar_strings(key, value) < rule["similar"]

        matrix = {"key": key, "value": value}
        checks = {
            "minlen": check_minlen,
            "regex": check_regex,
            "isBase64": check_isBase64,
            "isAscii": check_isAscii,
            "isUri": check_isUri,
        }
        for rule_id, rule in self.rules.items():
            rule_matched = True
            if rule["severity"] == "INFO":
                continue
            if "similar" in rule:
                if similar_strings(key, value) >= rule["similar"]:
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
                find_line_number(filepath, key, value),
                key,
                value,
                self.rules[rule_id]["message"],
                self.rules[rule_id]["severity"],
            )
