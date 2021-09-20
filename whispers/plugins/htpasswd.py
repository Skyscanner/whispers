from pathlib import Path
from typing import Iterator

from whispers.core.utils import KeyValuePair, strip_string


class Htpasswd:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        lineno = 0
        key = "htpasswd hash"

        for line in filepath.open("r").readlines():
            lineno += 1
            if ":" not in line:
                continue

            creds = line.split(":")
            value = strip_string(creds[1])
            if value:
                yield KeyValuePair(key, value, keypath=[key], line=lineno)
