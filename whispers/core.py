import re
from pathlib import Path

from whispers.log import debug
from whispers.secrets import WhisperSecrets
from whispers.utils import load_yaml_from_file


def load_config(configfile, src="."):
    configfile = Path(configfile)
    if not configfile.exists():
        debug(f"{configfile} does not exist")
        raise FileNotFoundError

    if not configfile.is_file():
        debug(f"{configfile} is not a file")
        raise TypeError

    config = load_yaml_from_file(configfile)

    # Ensure minimal expected config structure
    if "exclude" not in config:
        config["exclude"] = {"files": [], "keys": [], "values": []}
    else:
        for idx in ["files", "keys", "values"]:
            if idx not in config["exclude"]:
                config["exclude"][idx] = []
    if "include" not in config:
        config["include"] = {"files": ["**/*"]}
    elif "files" not in config["include"]:
        config["include"]["files"] = ["**/*"]

    # Glob excluded files
    exfiles = []
    for fileglob in config["exclude"]["files"]:
        for filepath in Path(src).glob(fileglob):
            exfiles.append(filepath)
    config["exclude"]["files"] = exfiles

    # Compile regex from excluded keys and values
    for param in ["keys", "values"]:
        excluded = []
        for item in config["exclude"][param]:
            excluded.append(re.compile(item, flags=re.IGNORECASE))
        config["exclude"][param] = excluded

    # Optional: rules
    if "rules" not in config:
        config["rules"] = {}

    return config


def run(src: str, config=None):
    src = Path(src)
    if not src.exists():
        debug(f"{src} does not exist")
        raise FileNotFoundError

    if src.is_file():
        files = [src.as_posix()]
    elif src.is_dir():
        files = []
    else:
        debug(f"{src} is neither a file nor a directory")
        raise TypeError

    # Configure execution
    if not config:
        configpath = Path(__file__).parent
        configfile = configpath.joinpath("config.yml").as_posix()
        config = load_config(configfile, src=src)

    # Include files
    for incfile in config["include"]["files"]:
        files += set(src.glob(incfile))

    # Exclude files
    files = list(set(files) - set(config["exclude"]["files"]))

    # Scan files
    whispers = WhisperSecrets(config)
    for filename in files:
        for secret in whispers.scan(filename):
            if secret:
                yield secret
