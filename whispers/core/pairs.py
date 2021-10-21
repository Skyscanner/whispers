import logging
from pathlib import Path
from typing import Iterator, Optional

from whispers.core.utils import KeyValuePair, is_base64_bytes, is_iac, is_path, simple_string, strip_string
from whispers.plugins.config import Config
from whispers.plugins.dockercfg import Dockercfg
from whispers.plugins.dockerfile import Dockerfile
from whispers.plugins.html import Html
from whispers.plugins.htpasswd import Htpasswd
from whispers.plugins.jproperties import Jproperties
from whispers.plugins.json import Json
from whispers.plugins.npmrc import Npmrc
from whispers.plugins.pip import Pip
from whispers.plugins.plaintext import Plaintext
from whispers.plugins.pypirc import Pypirc
from whispers.plugins.python import Python
from whispers.plugins.shell import Shell
from whispers.plugins.xml import Xml
from whispers.plugins.yml import Yml


def make_pairs(config: dict, file: Path) -> Optional[Iterator[KeyValuePair]]:
    """Generates KeyValuePair objects by parsing given file"""
    if not file.exists():
        return None

    if not file.is_file():
        return None

    # First, return file name to check if it is a sensitive file
    pair = KeyValuePair("file", file.as_posix(), keypath=["file"])
    if filter_included(config, pair):
        yield tag_file(file, pair)

    # Second, attempt to parse the file with a plugin
    plugin = load_plugin(file)
    if not plugin:
        return None

    logging.debug(f"Loaded plugin '{plugin}' for file '{file}'")

    pairs = plugin().pairs(file)
    static = filter(None, map(filter_static, pairs))
    included = filter(None, map(lambda pair: filter_included(config, pair), static))
    tagged = map(lambda pair: tag_file(file, pair), included)

    yield from tagged


def tag_file(file: Path, pair: KeyValuePair) -> KeyValuePair:
    """Add pair file path"""
    pair.file = file.as_posix()
    return pair


def filter_included(config: dict, pair: KeyValuePair) -> Optional[KeyValuePair]:
    """Check if pair should be included based on config"""
    for key in pair.keypath:
        if config["exclude"]["keys"].match(key):
            logging.debug(f"Excluded key {pair}")
            return None  # Excluded key

    if config["exclude"]["values"]:
        if config["exclude"]["values"].match(pair.value):
            logging.debug(f"Excluded value {pair}")
            return None  # Excluded value

    logging.debug(f"Included value {pair}")
    return pair  # Included value


def filter_static(pair: KeyValuePair) -> Optional[KeyValuePair]:
    """Check if pair contains hardcoded static values"""
    pair.key = strip_string(pair.key)
    pair.value = strip_string(pair.value)

    if not is_static(pair.key, pair.value):
        logging.debug(f"Dynamic value {pair}")
        return None  # Dynamic value

    logging.debug(f"Static value {pair}")
    return pair  # Static value


def is_static(key: str, value: str) -> bool:
    """Check if pair is static"""
    if not isinstance(value, str):
        return False  # Not string

    if not value:
        return False  # Empty

    if value.lower() == "null":
        return False  # Empty

    if value.startswith("$") and "$" not in value[2:]:
        return False  # Variable

    if value.startswith("%") and value.endswith("%"):
        return False  # Variable

    if value.startswith("${") and value.endswith("}"):
        return False  # Variable

    if value.startswith("{") and value.endswith("}"):
        if len(value) > 50:
            if is_base64_bytes(value[1:-1]):
                return True  # Token

        return False  # Variable

    if "{{" in value and "}}" in value:
        return False  # Variable

    if value.startswith("<") and value.endswith(">"):
        return False  # Placeholder

    s_key = simple_string(key)
    s_value = simple_string(value)

    if s_key == s_value:
        return False  # Placeholder

    if s_value.endswith(s_key):
        return False  # Placeholder

    if is_iac(value):
        return False  # IaC !Ref !Sub ...

    if is_path(value):
        return False  # System path

    return True  # Hardcoded static value


def load_plugin(file: Path) -> Optional[object]:
    """
    Loads the correct plugin for given file.
    Returns None if no plugin found.
    """
    if file.suffix in [".dist", ".template"]:
        filetype = file.stem.split(".")[-1]
    else:
        filetype = file.name.split(".")[-1]

    if filetype in ["yaml", "yml"]:
        return Yml

    elif filetype == "json":
        return Json

    elif filetype == "xml":
        return Xml

    elif filetype.startswith("npmrc"):
        return Npmrc

    elif filetype.startswith("pypirc"):
        return Pypirc

    elif file.name == "pip.conf":
        return Pip

    elif filetype in ["conf", "cfg", "cnf", "config", "ini", "env", "credentials", "s3cfg"]:
        with file.open("r") as fh:
            if fh.readline().startswith("<?xml "):
                return Xml

            else:
                return Config

    elif filetype == "properties":
        return Jproperties

    elif filetype.startswith(("sh", "bash", "zsh", "env")):
        return Shell

    elif "dockerfile" in file.name.lower():
        return Dockerfile

    elif filetype == "dockercfg":
        return Dockercfg

    elif filetype.startswith("htpasswd"):
        return Htpasswd

    elif filetype == "txt":
        return Plaintext

    elif filetype.startswith("htm"):
        return Html

    elif filetype in ["py", "py3", "py35", "py36", "py37", "py38", "py39"]:
        return Python

    return None
