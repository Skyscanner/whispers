from pathlib import Path

import astroid

from whispers.log import debug


class Python:
    def pairs(self, filepath: Path):
        """
        Parses Python source code into AST using Astroid
        http://pylint.pycqa.org/projects/astroid/en/latest/api/astroid.nodes.html#id1
        Returns key-value pairs
        """

        def is_key(node):
            types = [astroid.node_classes.Name, astroid.node_classes.AssignName]
            return type(node) in types

        def is_value(node):
            types = [astroid.node_classes.Const]
            return type(node) in types

        def _traverse(tree):
            for node in tree.get_children():
                yield from _traverse(node)
                # Assignment
                if isinstance(node, astroid.node_classes.Assign):
                    if not is_value(node.value):
                        continue
                    value = node.value.value
                    for key in node.targets:
                        if is_key(key):
                            yield key.name, value
                # Comparison
                elif isinstance(node, astroid.node_classes.Compare):
                    left = node.left
                    right = node.ops[0][1]
                    if is_key(left) and is_value(right):
                        key = left.name
                        value = right.value
                    elif is_key(right) and is_value(left):
                        key = right.name
                        value = left.value
                    else:
                        continue
                    yield key, value
                # Dictionary values
                elif isinstance(node, astroid.node_classes.Dict):
                    for key, value in node.items:
                        if not is_value(key) or not is_value(value):
                            continue
                        yield key.value, value.value
                # Keywords
                elif isinstance(node, astroid.node_classes.Keyword):
                    if is_value(node.value):
                        yield node.arg, node.value.value
                # Function call
                elif isinstance(node, astroid.node_classes.Call):
                    key = "function"
                    value = node.as_string()  # Entire function call
                    yield key, value

        try:
            tree = astroid.parse(filepath.read_text())
            yield from _traverse(tree)
        except Exception as e:
            debug(f"{type(e)} in {filepath}")
