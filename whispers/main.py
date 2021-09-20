import sys
from argparse import Namespace
from itertools import chain
from os import environ
from typing import Iterator

from whispers.core.args import parse_args
from whispers.core.config import load_config
from whispers.core.log import cleanup_log, configure_log
from whispers.core.pairs import make_pairs
from whispers.core.printer import printer
from whispers.core.rules import load_rules
from whispers.core.scope import load_scope
from whispers.core.secrets import detect_secrets
from whispers.core.utils import KeyValuePair

environ["PYTHONIOENCODING"] = "UTF-8"


def cli():  # pragma: no cover
    """Main method when executing from CLI given argv"""
    args = parse_args()
    secrets = run(args)
    list(map(lambda secret: printer(args, secret), secrets))
    cleanup_log()
    sys.exit(args.exitcode)


def run(args: Namespace) -> Iterator[KeyValuePair]:
    """Main method for getting secrets given args"""
    configure_log(args)

    config = load_config(args)
    rules = load_rules(args, config)
    scope = load_scope(args, config)
    parsed = map(lambda file: make_pairs(config, file), scope)
    detected = map(lambda pairs: detect_secrets(rules, pairs), parsed)
    secrets = chain.from_iterable(detected)

    return secrets


if __name__ == "__main__":
    cli()
