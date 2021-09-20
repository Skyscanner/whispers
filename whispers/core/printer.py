import json
from argparse import Namespace

from whispers.core.utils import KeyValuePair


def printer(args: Namespace, pair: KeyValuePair) -> str:
    """Prints formatted pair data to given output"""
    fmt = json.dumps(
        {
            "key": pair.key,
            "value": pair.value,
            "file": pair.file,
            "line": pair.line,
            "rule_id": pair.rule["id"],
            "message": pair.rule["message"],
            "severity": pair.rule["severity"],
        }
    )

    print(fmt, file=args.output)
    return fmt
