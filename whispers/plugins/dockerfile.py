from pathlib import Path
from typing import Iterator

from whispers.core.utils import KeyValuePair


class Dockerfile:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        for lineno, line in enumerate(filepath.open(), 1):
            # ENV key=value
            if line.startswith("ENV "):
                item = line.replace("ENV ", "", 1)
                for op in ["=", " "]:
                    if op in item and len(item.split(op)) == 2:
                        key, value = item.split(op)
                        yield KeyValuePair(key, value, keypath=[key], line=lineno)
