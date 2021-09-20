from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse

from whispers.core.utils import KeyValuePair


class Pip:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        lineno = 0
        key = "pip password"

        for line in filepath.open("r").readlines():
            lineno += 1
            if "http" not in line:
                continue

            value = urlparse(line.split("=")[-1].strip()).password
            if value:
                yield KeyValuePair(key, value, keypath=[key], line=lineno)
