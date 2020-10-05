from pathlib import Path

from whispers.utils import strip_string


class Javascript:
    def pairs(self, filepath: Path):
        for line in filepath.open("r").readlines():
            if "=" in line:
                yield from self.parse_assignment(line)

    def parse_assignment(self, line: str):
        key, value = line.split("=")
        value = strip_string(value.replace(";", ""))
        yield key, value
