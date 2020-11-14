from pathlib import Path

import astroid

from whispers.log import debug


class Python:
    """
    Parses Python source code into AST using Astroid
    http://pylint.pycqa.org/projects/astroid/en/latest/api/astroid.nodes.html#id1
    Returns key-value pairs
    """

    def pairs(self, filepath: Path):
        try:
            tree = astroid.parse(filepath.read_text())
            yield from self.traverse(tree)
        except Exception as e:
            debug(f"{type(e)} in {filepath}")

    @staticmethod
    def is_key(node):
        types = [astroid.node_classes.Name, astroid.node_classes.AssignName]
        return type(node) in types

    @staticmethod
    def is_value(node):
        types = [astroid.node_classes.Const]
        return type(node) in types

    def traverse(self, tree):
        for node in tree.get_children():
            yield from self.traverse(node)
            # Assignment
            if isinstance(node, astroid.node_classes.Assign):
                if not self.is_value(node.value):
                    continue
                value = node.value.value
                for key in node.targets:
                    if self.is_key(key):
                        yield key.name, value
            # Comparison
            elif isinstance(node, astroid.node_classes.Compare):
                left = node.left
                right = node.ops[0][1]
                if self.is_key(left) and self.is_value(right):
                    key = left.name
                    value = right.value
                elif self.is_key(right) and self.is_value(left):
                    key = right.name
                    value = left.value
                else:
                    continue
                yield key, value
            # Dictionary values
            elif isinstance(node, astroid.node_classes.Dict):
                for key, value in node.items:
                    if not self.is_value(key) or not self.is_value(value):
                        continue
                    yield key.value, value.value
            # Keywords
            elif isinstance(node, astroid.node_classes.Keyword):
                if self.is_value(node.value):
                    yield node.arg, node.value.value
            # Function call
            elif isinstance(node, astroid.node_classes.Call):
                key = "function"
                value = node.as_string()  # Entire function call
                yield key, value
                yield from self.parse_env_functions(node)

    def parse_env_functions(self, node: astroid.node_classes.Call):
        envfuncs = [
            "getenv",
            "environ.get",
        ]
        node_name = node.func.as_string()
        if any(name in node_name for name in envfuncs):
            if len(node.args) == 2:
                key, value = node.args
                if self.is_value(key) and self.is_value(value):
                    yield key.value, value.value
