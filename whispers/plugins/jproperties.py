from pathlib import Path

from jproperties import Properties


class Jproperties:
    def pairs(self, filepath: Path):
        props = Properties()
        props.load(filepath.read_text(), "utf-8")
        for key, value in props.properties.items():
            key = key.replace(".", "_")
            yield key, value
