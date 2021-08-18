import json
from pathlib import Path


class Dockercfg:
    def pairs(self, filepath: Path):
        config = json.loads(filepath.read_text())
        if "auths" not in config:
            return

        for auth in config["auths"].values():
            if "auth" not in auth:
                continue

            token = auth["auth"]

            yield "Dockercfg", token
