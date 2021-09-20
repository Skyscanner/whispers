import json
from pathlib import Path
from typing import Iterator

from whispers.core.utils import KeyValuePair


class Dockercfg:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        config = json.loads(filepath.read_text())
        key = "auth"
        keypath = ["auths", key]

        if "auths" not in config:
            return

        for auth in config["auths"].values():
            if key not in auth:
                continue

            token = auth[key]
            yield KeyValuePair("dockercfg auth", token, keypath)
