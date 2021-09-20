import json
import re
from pathlib import Path
from typing import Iterator

from whispers.core.log import global_exception_handler
from whispers.core.utils import KeyValuePair
from whispers.plugins.traverse import StructuredDocument


class Json(StructuredDocument):
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
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
        except Exception:
            global_exception_handler(filepath.as_posix(), document)
