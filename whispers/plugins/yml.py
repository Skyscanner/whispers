import re
from pathlib import Path

import yaml

from whispers.log import debug
from whispers.plugins.traverse import StructuredDocument


class Yml(StructuredDocument):
    def pairs(self, filepath: Path):
        def _constructor(loader, tag_suffix, node):
            """This is needed to parse IaC syntax"""
            if isinstance(node, yaml.MappingNode):
                return loader.construct_mapping(node)
            if isinstance(node, yaml.SequenceNode):
                return loader.construct_sequence(node)
            ret = loader.construct_scalar(node)
            return f"{tag_suffix} {ret}"

        """
        Convert custom YAML to parsable YAML
        - Skip ---
        - Quote unquoted values such as {{ placeholder }}
        - Remove text between <% %> and {% %}
        - Remove comments that start with #
        """
        document = ""
        for line in filepath.open("r").readlines():
            if line.startswith("---"):
                continue
            if re.match(r".+(\[)?\{\{.*\}\}(\])?", line):
                line = line.replace('"', "'")
                line = line.replace("{{", '"{{').replace("}}", '}}"')
            document += line
        document = re.sub(r"[<{]%.*?%[}>]", "", document, flags=re.MULTILINE | re.DOTALL)
        document = re.sub(r"^#.*$", "", document)

        # Load converted YAML
        yaml.add_multi_constructor("", _constructor, Loader=yaml.SafeLoader)
        try:
            code = yaml.safe_load(document)
            yield from self.traverse(code)
        except Exception as e:
            debug(f"{type(e)} in {filepath}")
