from pathlib import Path


class Npmrc:
    def pairs(self, filepath: Path):
        for line in filepath.open("r").readlines():
            if ":_authToken=" not in line:
                continue

            value = line.split(":_authToken=")[-1].strip()
            if value:
                yield "npm_authToken", value
