from pathlib import Path

from whispers.utils import strip_string


class Htpasswd:
    def pairs(self, filepath: Path):
        for line in filepath.open("r").readlines():
            if ":" not in line:
                continue
            creds = line.split(":")
            value = strip_string(creds[1])
            if value:
                yield "htpasswd_Hash", value
