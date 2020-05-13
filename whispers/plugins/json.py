import json
import re
from pathlib import Path

from whispers.log import debug
from whispers.plugins.traverse import StructuredDocument


class Json(StructuredDocument):
    def pairs(self, filepath: Path):
        """
        Convert custom JSON to parsable JSON
        - Remove lines that start with // comments
        - Strip // comments from the end the line
        """
        document = ""
        for line in filepath.open("r").readlines():
            if line.startswith("//"):
                continue
            line = re.sub(r" // ?.*$", "", line)
            document += line

        # Load converted JSON
        try:
            document = json.loads(document)
            yield from self.traverse(document)
        except Exception as e:
            debug(f"{type(e)} in {filepath}")
