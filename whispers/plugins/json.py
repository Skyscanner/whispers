import json
import re
from pathlib import Path

from whispers.log import debug
from whispers.plugins.traverse import StructuredDocument


class Json(StructuredDocument):
    def pairs(self, filepath: Path):
        """
        Convert custom JSON to parsable JSON
        - Remove comments that start with //
        """
        document = filepath.read_text()
        document = re.sub(r"^//.*", "", document, flags=re.MULTILINE | re.DOTALL)

        # Load converted JSON
        try:
            document = json.loads(document)
            yield from self.traverse(document)
        except Exception as e:
            debug(f"{type(e)} in {filepath}")
