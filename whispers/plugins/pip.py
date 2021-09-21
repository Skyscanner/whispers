from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse

from whispers.core.utils import KeyValuePair


class Pip:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        for lineno, line in enumerate(filepath.open(), 1):
            if "http" not in line:
                continue

            value = urlparse(line.split("=")[-1].strip()).password
            if value:
                key = "pip password"
                yield KeyValuePair(key, value, keypath=[key], line=lineno)
