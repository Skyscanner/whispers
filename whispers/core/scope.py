from argparse import Namespace
from pathlib import Path
from typing import Iterator


def load_scope(args: Namespace, config: dict) -> Iterator[Path]:
    """Load a list of files in scope based on args and config"""
    src = Path(args.src)
    included = config["include"]["files"]
    excluded = config["exclude"]["files"]

    if src.is_file():
        yield src

    else:
        for include in included:
            for path in src.rglob(include):
                if excluded and excluded.match(path.as_posix()):
                    continue

                yield path
