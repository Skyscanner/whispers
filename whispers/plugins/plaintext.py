from pathlib import Path

from whispers.plugins.uri import Uri
from whispers.rules import WhisperRules
from whispers.utils import strip_string


class Plaintext:
    def __init__(self):
        self.rules = WhisperRules()

    def pairs(self, filepath: Path):
        lines = filepath.open("r").readlines()
        for idx in range(len(lines)):
            line = lines[idx]
            if not strip_string(line):
                continue

            for value in line.split():
                if self.rules.match("uri", value):
                    yield from Uri().pairs(value)
