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
    def is_key(node) -> bool:
        """
        Check if node is a variable
        """
        types = [astroid.node_classes.Name, astroid.node_classes.AssignName]
        return type(node) in types

    @staticmethod
    def is_value(node) -> bool:
        """
        Check if node is a value
        """
        types = [astroid.node_classes.Const, astroid.node_classes.JoinedStr, astroid.node_classes.Call]
        return type(node) in types

    @staticmethod
    def node_concat_const(nodes) -> str:
        """
        Joins all Const node values and returns as string
        Return empty string if a non-Const node is found
        """
        ret = ""
        for value in nodes:
            if not isinstance(value, astroid.node_classes.Const):
                return ""
            ret += value.value
        return ret

    def node_to_str(self, node) -> str:
        """
        Converts node valid objects to string
        Returns empty string otherwise
        """
        if isinstance(node, astroid.node_classes.Name):
            return node.name
        if isinstance(node, astroid.node_classes.AssignName):
            return node.name
        if isinstance(node, astroid.node_classes.Const):
            return node.value
        if isinstance(node, astroid.node_classes.JoinedStr):
            return self.node_concat_const(node.values)
        if isinstance(node, astroid.node_classes.Keyword):
            return node.arg
        if isinstance(node, astroid.node_classes.Call):
            return self.node_concat_const(node.args)
        return ""

    def traverse(self, tree):
        """
        Recursively traverse nodes yielding key-value pairs
        """
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
                key, value = "", ""
                if self.is_key(left) and self.is_value(right):
                    key = self.node_to_str(left)
                    value = self.node_to_str(right)
                elif self.is_key(right) and self.is_value(left):
                    key = self.node_to_str(right)
                    value = self.node_to_str(left)
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
                key = self.node_to_str(node)
                value = self.node_to_str(node.value)
                if key and value:
                    yield key, value
            # Function call
            elif isinstance(node, astroid.node_classes.Call):
                key = "function"
                value = node.as_string()  # Entire function call
                yield key, value
                yield from self.parse_env_functions(node)

    def parse_env_functions(self, node: astroid.node_classes.Call):
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
                    yield key, value
