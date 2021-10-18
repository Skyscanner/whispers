import logging
from argparse import ArgumentParser, Namespace
from functools import wraps
from sys import argv, stdout

from whispers.__version__ import __version__, __whispers__
from whispers.core.rules import default_rules, list_rule_ids
from whispers.core.utils import DEFAULT_SEVERITY


def argument_parser() -> ArgumentParser:
    """CLI argument parser"""
    args_parser = ArgumentParser("whispers", description=("Identify secrets in static structured text."))
    args_parser.add_argument("-v", "--version", action="version", version=__version__)
    args_parser.add_argument("-i", "--info", action="store_true", help="show extended help and exit")
    args_parser.add_argument("-c", "--config", help="config file")
    args_parser.add_argument("-o", "--output", help="output file")
    args_parser.add_argument("-e", "--exitcode", default=0, type=int, help="exit code on success")
    args_parser.add_argument("-r", "--rules", help="comma-separated list of rule IDs (see --info)")
    args_parser.add_argument("-s", "--severity", help="comma-separated list of severity levels to report (see --info)")
    args_parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
        help="show debugging information",
    )
    args_parser.add_argument("src", nargs="?", help="target file or directory")

    args_parser.print_help = show_splash(args_parser.print_help)

    return args_parser


def parse_args(arguments: list = argv[1:]) -> Namespace:
    """Parses a list into a namespace"""
    args, _ = argument_parser().parse_known_args(arguments)

    if args.info:
        show_info()
        exit()

    if not args.src:
        argument_parser().print_help()
        exit()

    if args.output:
        args.output = open(args.output, "w")
    else:
        args.output = stdout

    if args.rules:
        args.rules = args.rules.split(",")

    if args.severity:
        args.severity = args.severity.split(",")

    return args


def show_splash(func, **kwargs):
    @wraps(func)
    def splash(*args, **kwargs):
        print(__whispers__)
        print(__version__.rjust(64), end="\n\n")
        return func(*args, **kwargs)

    return splash


def show_info():
    argument_parser().print_help()
    print("\ndefault rule IDs:")
    list(map(lambda x: print(f"  - {x}"), list_rule_ids(default_rules())))
    print("\ndefault severity levels:")
    list(map(lambda x: print(f"  - {x}"), DEFAULT_SEVERITY))
