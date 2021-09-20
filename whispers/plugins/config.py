from pathlib import Path
from typing import Iterator

from whispers.core.utils import KeyValuePair, strip_string


class Config:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        for lineno, line in enumerate(filepath.open(), 1):
            line = line.strip()
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = strip_string(key)
            value = strip_string(value)

            if value:
                yield KeyValuePair(key, value, keypath=[key], line=lineno)
