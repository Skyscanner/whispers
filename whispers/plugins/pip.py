from pathlib import Path
from urllib.parse import urlparse


class Pip:
    def pairs(self, filepath: Path):
        for line in filepath.open("r").readlines():
            if "http" not in line:
                continue

            value = urlparse(line.split("=")[-1].strip()).password
            if value:
                yield "pip_Password", value
