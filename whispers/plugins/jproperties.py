from pathlib import Path
from typing import Iterator

from jproperties import Properties

from whispers.core.utils import KeyValuePair


class Jproperties:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        props = Properties()
        props.load(filepath.read_text(), "utf-8")
        for key, value in props.properties.items():
            key = key.replace(".", "_")
            yield KeyValuePair(key, value, [key])
