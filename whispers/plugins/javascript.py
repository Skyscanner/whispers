from pathlib import Path

from whispers.utils import strip_string


class Javascript:
    def pairs(self, filepath: Path):
        for line in filepath.open("r").readlines():
            if line.count("=") == 1:
                yield from self.parse_assignment(line)

    def parse_assignment(self, line: str):
        key, value = line.split("=")
        value = strip_string(value.replace(";", ""))
        if not self.is_function(value):
            yield key, value

    def is_function(self, value: str) -> bool:
        open_brackets = value.count("(")
        close_brackets = value.count(")")
        if open_brackets:
            if open_brackets == close_brackets:
                return True
        return False
