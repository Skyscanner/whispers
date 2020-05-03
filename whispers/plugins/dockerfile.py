from pathlib import Path


class Dockerfile:
    def pairs(self, filepath: Path):
        for line in filepath.open("r").readlines():
            # ENV key=value
            if line.startswith("ENV "):
                item = line.replace("ENV ", "", 1)
                for op in ["=", " "]:
                    if op in item and len(item.split(op)) == 2:
                        key, value = item.split(op)
                        yield key, value
