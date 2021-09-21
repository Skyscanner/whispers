from pathlib import Path
from typing import Iterator

from whispers.core.utils import KeyValuePair


class Pypirc:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        for lineno, line in enumerate(filepath.open(), 1):
            if "password:" not in line:
                continue

            value = line.split("password:")[-1].strip()
            if value:
                key = "pypi password"
                yield KeyValuePair(key, value, keypath=[key], line=lineno)
