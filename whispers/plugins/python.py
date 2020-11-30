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
    def is_value(node) -> bool:
        types = [astroid.node_classes.Const, astroid.node_classes.JoinedStr]
        return type(node) in types

    @staticmethod
    def node_concat_const(nodes) -> str:
        ret = ""
        for value in nodes:
            if not isinstance(value, astroid.node_classes.Const):
                return ""
            ret += value.value
        return ret

    def node_to_str(self, node) -> str:
        if isinstance(node, astroid.node_classes.Name):
            return node.name
        if isinstance(node, astroid.node_classes.AssignName):
            return node.name
        if isinstance(node, astroid.node_classes.Const):
            return node.value
        if isinstance(node, astroid.node_classes.Assign):
            return node.value
        if isinstance(node, astroid.node_classes.JoinedStr):
            return self.node_concat_const(node.values)
        if isinstance(node, astroid.node_classes.Call):
            return self.node_concat_const(node.args)
        return ""

    def traverse(self, tree):
        for node in tree.get_children():
            yield from self.traverse(node)
            # Assignment
            if isinstance(node, astroid.node_classes.Assign):
                if not self.is_value(node.value):
                    continue
                value = self.node_to_str(node.value)
                for key in node.targets:
                    key = self.node_to_str(key)
                    if key and value:
                        yield key, value
            # Comparison
            elif isinstance(node, astroid.node_classes.Compare):
                left = node.left
                right = node.ops[0][1]
                if self.is_key(left):
                    key = self.node_to_str(left)
                    value = self.node_to_str(right)
                elif self.is_key(right):
                    key = self.node_to_str(right)
                    value = self.node_to_str(left)
                else:
                    continue
                if key and value:
                    yield key, value
            # Dictionary values
            elif isinstance(node, astroid.node_classes.Dict):
                for key, value in node.items:
                    key = self.node_to_str(key)
                    value = self.node_to_str(value)
                    if key and value:
                        yield key, value
            # Keywords
            elif isinstance(node, astroid.node_classes.Keyword):
                value = self.node_to_str(node)
                if value:
                    yield node.arg, value
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
