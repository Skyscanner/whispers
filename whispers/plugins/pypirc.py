from pathlib import Path
from typing import Iterator

from whispers.core.utils import KeyValuePair


class Pypirc:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        lineno = 0
        key = "pypi password"

        for line in filepath.open("r").readlines():
            lineno += 1
            if "password:" not in line:
                continue

            value = line.split("password:")[-1].strip()
            if value:
                yield KeyValuePair(key, value, keypath=[key], line=lineno)
