import logging
import re
from argparse import Namespace
from pathlib import Path

from whispers.core.rules import default_rules, list_rule_ids
from whispers.core.utils import DEFAULT_PATH, DEFAULT_SEVERITY, ensure_file_exists, load_yaml_from_file


def load_config(args: Namespace) -> dict:
    """Load config given args"""
    if args.config:
        configfile = Path(args.config)
    else:
        configfile = DEFAULT_PATH.joinpath("config.yml")

    ensure_file_exists(configfile)
    config = load_yaml_from_file(configfile)
    default_config_structure(config)

    logging.debug(f"Loaded config '{config}'")
    return config


def default_config_structure(config: dict):
    """Ensure minimal expected config structure"""
    try:
        config["include"] = config.get("include", {"files": ["**/*"]})
        config["include"]["files"] = config["include"].get("files", ["**/*"])

        config["exclude"] = config.get("exclude", {"files": None, "keys": None, "values": None})
        config["exclude"]["files"] = config["exclude"].get("files", None)
        config["exclude"]["keys"] = config["exclude"].get("keys", None)
        config["exclude"]["values"] = config["exclude"].get("values", None)

        for idx in ["files", "keys", "values"]:
            if not config["exclude"][idx]:
                continue

            # Create a single regex statement and compile it for efficient matching
            unified = "|".join(config["exclude"][idx])
            config["exclude"][idx] = re.compile(unified)

        config["severity"] = config.get("severity", DEFAULT_SEVERITY)
        config["rules"] = config.get("rules", list_rule_ids(default_rules()))

    except Exception:
        raise NameError("Invalid config")
