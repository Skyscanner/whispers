from typing import Iterator

from whispers.core.utils import KeyValuePair, is_uri
from whispers.plugins.uri import Uri


class StructuredDocument:
    def __init__(self):
        self.keypath = []

    def traverse(self, code, key=None):
        """Recursively traverse YAML/JSON document"""
        if isinstance(code, dict):
            yield from self.cloudformation(code)

            for k, v in code.items():
                self.keypath.append(k)
                if isinstance(v, (str, int)):
                    yield KeyValuePair(k, v, list(self.keypath))

                yield from self.traverse(v, key=k)
                self.keypath.pop()

            # Special key/value format
            elements = list(code.keys())
            if "key" in elements and "value" in elements:
                yield KeyValuePair(code["key"], code["value"], list(self.keypath))

        elif isinstance(code, list):
            for item in code:
                if isinstance(item, (str, int)):
                    yield KeyValuePair(key, item, list(self.keypath))

                yield from self.traverse(item, key=key)

        elif isinstance(code, str):
            if "=" in code:
                item = code.split("=")
                if len(item) == 2:
                    yield KeyValuePair(item[0], item[1], list(self.keypath))

            if is_uri(code):
                for pair in Uri().pairs(code):
                    pair.keypath = list(self.keypath)
                    yield pair

    def cloudformation(self, code: dict) -> Iterator[KeyValuePair]:
        """AWS CloudFormation format"""
        if self.keypath:
            return  # Not tree root

        if "AWSTemplateFormatVersion" not in code:
            return  # Not CF format

        if "Parameters" not in code:
            return  # No parameters

        for key, values in code["Parameters"].items():
            if "Default" not in values:
                continue  # No default value

            keypath = ["Parameters", "Default", key]
            yield KeyValuePair(key, values["Default"], keypath)
