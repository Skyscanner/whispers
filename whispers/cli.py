from argparse import ArgumentParser, Namespace
from os import environ
from pathlib import Path

from whispers.__version__ import __version__
from whispers.core import load_config, run
from whispers.log import cleanup_log, configure_log
from whispers.rules import WhisperRules
from whispers.utils import format_stdout

environ["PYTHONIOENCODING"] = "UTF-8"


def cli_parser() -> ArgumentParser:
    args_parser = ArgumentParser("whispers", description=("Identify secrets and dangerous behaviours"))
    args_parser.add_argument("-v", "--version", action="version", version=f"whispers {__version__}")
    args_parser.add_argument("-i", "--info", action="store_true", default=False, help="show extended help and exit")
    args_parser.add_argument("-c", "--config", default=None, help="config file (.yml)")
    args_parser.add_argument("-r", "--rules", default="all", help="comma-separated rule ID list")
    args_parser.add_argument("-o", "--output", help="output file (.yml)")
    args_parser.add_argument("src", nargs="?", help="target file or directory")
    return args_parser


def parse_args(arguments=None) -> Namespace:
    args, _ = cli_parser().parse_known_args(arguments)
    return args


def cli(arguments=None):
    # Parse CLI arguments
    args = parse_args(arguments)

    # Show information
    if args.info:
        exit(cli_info())

    # Default response
    if not args.src:
        exit(cli_parser().print_help())

    # Clear output file
    if args.output:
        args.output = Path(args.output)
        args.output.write_text("")

    # Configure execution
    configure_log()
    if args.config:
        args.config = load_config(args.config, src=args.src)

    # Valar margulis
    for secret in run(args):
        format_stdout(secret, args.output)

    # Clean up
    cleanup_log()


def cli_info():
    rule_ids = list(WhisperRules().rules.keys())
    rule_ids.sort()
    cli_parser().print_help()
    print("\navailable rules:")
    for rule_id in rule_ids:
        print(f"  {rule_id}")


if __name__ == "__main__":
    cli()
