from pathlib import Path
from typing import Iterator

from whispers.core.utils import KeyValuePair


class Npmrc:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        lineno = 0
        key = "npm authToken"

        for line in filepath.open("r").readlines():
            lineno += 1
            if ":_authToken=" not in line:
                continue

            value = line.split(":_authToken=")[-1].strip()
            if value:
                yield KeyValuePair(key, value, keypath=[key], line=lineno)
