from pathlib import Path
from typing import Iterator

from whispers.core.utils import KeyValuePair


class Npmrc:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        for lineno, line in enumerate(filepath.open(), 1):
            if ":_authToken=" not in line:
                continue

            value = line.split(":_authToken=")[-1].strip()
            if value:
                key = "npm authToken"
                yield KeyValuePair(key, value, keypath=[key], line=lineno)
