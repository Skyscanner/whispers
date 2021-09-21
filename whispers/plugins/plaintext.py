from pathlib import Path
from typing import Iterator

from whispers.core.utils import KeyValuePair, is_uri, strip_string
from whispers.plugins.uri import Uri


class Plaintext:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        for lineno, line in enumerate(filepath.open(), 1):
            if not strip_string(line):
                continue

            for value in line.split():
                if is_uri(value):
                    for pair in Uri().pairs(value):
                        pair.line = lineno
                        yield pair
