from pathlib import Path

from whispers.utils import string_is_function, string_is_quoted


class Go:
    def pairs(self, filepath: Path):
        for line in filepath.open("r").readlines():
            if not ("=" in line or ":=" in line):
                continue
            yield from self.parse_assignment(line)

    def parse_assignment(self, line: str):
        line = line.replace(":=", "=")
        key, value = line.split("=")
        key = key.strip()
        value = value.strip()
        if string_is_function(value):
            return
        if key.startswith(("var ", "const ")):
            key = " ".join(key.split(" ")[1:])
        if "," in value:
            keys = key.split(",")
            values = value.split(",")
        else:
            keys = [key]
            values = [value]
        for i in range(len(values)):
            key = keys[i].strip().split(" ")[0]
            value = values[i].strip()
            if string_is_quoted(value):
                yield key, value
