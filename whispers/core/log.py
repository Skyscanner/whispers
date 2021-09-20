import logging
import logging.config
from argparse import Namespace
from os import remove
from pathlib import Path


def configure_log(args: Namespace) -> Path:
    """Configure logging"""
    logpath = Path("whispers.log")
    logpath.write_text("")

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "class": "logging.Formatter",
                    "style": "{",
                    "datefmt": "%Y-%m-%d %H:%M",
                    "format": "[{asctime:s}] {message:s}",
                }
            },
            "handlers": {
                "default": {
                    "level": args.debug,
                    "class": "logging.handlers.WatchedFileHandler",
                    "formatter": "default",
                    "filename": logpath.as_posix(),
                    "mode": "w",
                    "encoding": "utf-8",
                }
            },
            # root logger
            "loggers": {"": {"handlers": ["default"], "level": args.debug, "propagate": False}},
        }
    )

    return logpath


def cleanup_log():
    """Delete the log file if it's empty"""
    logpath = Path("whispers.log")
    if not logpath.stat().st_size:
        remove(logpath.as_posix())


def global_exception_handler(file: str, data: str):
    logging.exception(f"{file}\n{data}")
