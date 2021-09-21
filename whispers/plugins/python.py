from pathlib import Path
from typing import Iterator, Tuple

import astroid

from whispers.core.log import global_exception_handler
from whispers.core.utils import KeyValuePair


class Python:
    """
    Parses Python source code into AST using Astroid
    http://pylint.pycqa.org/projects/astroid/en/latest/api/astroid.nodes.html#id1
    Returns key-value pairs
    """

    def __init__(self):
        self.keypath = []

    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        try:
            code = filepath.read_text()
            tree = astroid.parse(code)
            yield from self.traverse(tree)
        except Exception:
            global_exception_handler(filepath.as_posix(), code[:100])

    @staticmethod
    def is_key(node) -> bool:
        """
        Check if node is a variable
        """
        types = [astroid.nodes.Name, astroid.nodes.AssignName]
        return type(node) in types

    @staticmethod
    def is_value(node) -> bool:
        """
        Check if node is a value
        """
        types = [astroid.nodes.Const, astroid.nodes.JoinedStr, astroid.nodes.Call]
        return type(node) in types

    @staticmethod
    def node_concat_const(nodes) -> str:
        """
        Joins all Const node values and returns as string
        Return empty string if a non-Const node is found
        """
        ret = ""
        for value in nodes:
            if not isinstance(value, astroid.nodes.Const):
                return ""
            ret += f"{value.value}"
        return ret

    def node_to_str(self, node) -> str:
        """
        Converts node valid objects to string
        Returns empty string otherwise
        """
        if isinstance(node, astroid.nodes.Name):
            return node.name
        if isinstance(node, astroid.nodes.AssignName):
            return node.name
        if isinstance(node, astroid.nodes.Const):
            return node.value
        if isinstance(node, astroid.nodes.JoinedStr):
            return self.node_concat_const(node.values)
        if isinstance(node, astroid.nodes.Keyword):
            return node.arg
        if isinstance(node, astroid.nodes.Call):
            return self.node_concat_const(node.args)
        return ""

    def traverse(self, tree) -> Iterator[Tuple]:
        """
        Recursively traverse nodes yielding key-value pairs
        """
        for node in tree.get_children():
            yield from self.traverse(node)

            # Assignment
            if isinstance(node, astroid.nodes.Assign):
                if not self.is_value(node.value):
                    continue

                value = self.node_to_str(node.value)
                for key in node.targets:
                    key = self.node_to_str(key)
                    if key and value and isinstance(value, (str, int)):
                        yield KeyValuePair(key, value, keypath=[key], line=node.lineno)

            # Comparison
            elif isinstance(node, astroid.nodes.Compare):
                left = node.left
                right = node.ops[0][1]
                key, value = "", ""
                if self.is_key(left) and self.is_value(right):
                    key = self.node_to_str(left)
                    value = self.node_to_str(right)

                elif self.is_key(right) and self.is_value(left):
                    key = self.node_to_str(right)
                    value = self.node_to_str(left)

                if key and value and isinstance(value, (str, int)):
                    yield KeyValuePair(key, value, keypath=[key], line=node.lineno)

            # Dictionary values
            elif isinstance(node, astroid.nodes.Dict):
                for key, value in node.items:
                    if not self.is_value(value):
                        continue

                    key = self.node_to_str(key)
                    value = self.node_to_str(value)
                    if key and value and isinstance(value, (str, int)):
                        yield KeyValuePair(key, value, keypath=[key], line=node.lineno)

            # Keywords
            elif isinstance(node, astroid.nodes.Keyword):
                key = self.node_to_str(node)
                value = self.node_to_str(node.value)
                if key and value and isinstance(value, (str, int)):
                    yield KeyValuePair(key, value, keypath=[key], line=node.lineno)

            # Function call
            elif isinstance(node, astroid.nodes.Call):
                key = "function"
                value = node.as_string()  # Entire function call
                yield KeyValuePair(key, value, keypath=[key], line=node.lineno)
                yield from self.parse_env_functions(node)

    def parse_env_functions(self, node: astroid.nodes.Call):
        """
        Decompose environment calls into key-value pairs
        """
        envfuncs = [
            "getenv",
            "environ.get",
        ]
        node_name = node.func.as_string()
        if any(name in node_name for name in envfuncs):
            if len(node.args) == 2:
                key, value = node.args
                key = self.node_to_str(key)
                value = self.node_to_str(value)
                if key and value:
                    yield KeyValuePair(key, value, keypath=[key], line=node.lineno)
