from whispers.plugins.uri import Uri
from whispers.rules import WhisperRules


class StructuredDocument:
    def __init__(self):
        self.breadcrumbs = []
        self.rules = WhisperRules()

    def traverse(self, code, key=None):
        """Recursively traverse YAML/JSON document"""
        if isinstance(code, dict):
            yield from self.cloudformation(code)
            for k, v in code.items():
                self.breadcrumbs.append(k)
                yield k, v, self.breadcrumbs
                yield from self.traverse(v, key=k)
                self.breadcrumbs.pop()
            # Special key/value format
            elements = list(code.keys())
            if "key" in elements and "value" in elements:
                yield code["key"], code["value"], self.breadcrumbs
        elif isinstance(code, list):
            for item in code:
                yield key, item, self.breadcrumbs
                yield from self.traverse(item, key=key)
        elif isinstance(code, str):
            if "=" in code:
                item = code.split("=", 1)
                if len(item) == 2:
                    yield item[0], item[1], self.breadcrumbs
            if self.rules.match("uri", code):
                for k, v in Uri().pairs(code):
                    yield k, v, self.breadcrumbs

    def cloudformation(self, code):
        """
        AWS CloudFormation format
        """
        if self.breadcrumbs:
            return  # Not tree root
        if "AWSTemplateFormatVersion" not in code:
            return  # Not CF format
        if "Parameters" not in code:
            return  # No parameters
        for key, values in code["Parameters"].items():
            if "Default" not in values:
                continue  # No default value
            yield key, values["Default"]
