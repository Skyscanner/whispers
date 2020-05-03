from argparse import ArgumentParser
from pathlib import Path

from whispers.__version__ import __version__
from whispers.core import load_config, run
from whispers.log import configure_log
from whispers.utils import format_stdout


def cli():
    # Parse CLI arguments
    args_parser = ArgumentParser("whispers", description=("Identify secrets and dangerous behaviours"))
    args_parser.add_argument("-v", "--version", action="version", version=f"whispers {__version__}")
    args_parser.add_argument("-c", "--config", default=None, help="config file")
    args_parser.add_argument("-o", "--output", help="output file (.yml)")
    args_parser.add_argument("src", nargs="?", help="source code file or directory")
    args = args_parser.parse_args()

    # Default response
    if not args.src:
        exit(args_parser.print_help())

    # Clear output file
    if args.output:
        args.output = Path(args.output)
        args.output.write_text("")

    # Configure execution
    configure_log()
    if args.config:
        args.config = load_config(args.config, src=args.src)

    # Valar margulis
    for secret in run(args.src, config=args.config):
        format_stdout(secret, args.output)


if __name__ == "__main__":
    cli()
