from pathlib import Path


class Config:
    def pairs(self, filepath: Path):
        for line in filepath.open("r").readlines():
            if "=" not in line:
                continue
            if line.index("=") == len(line) - 1:
                continue

            item = line.strip().split("=", 1)
            yield item[0], item[1]
