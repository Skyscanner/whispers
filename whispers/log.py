import logging
import logging.config
import traceback
from os import remove
from pathlib import Path


def configure_log(logpath: str = "") -> Path:
    try:
        logpath = Path(logpath, "whispers.log")
        logpath.write_text("")
    except Exception:
        debug(f"{logpath} is not valid")
        raise ValueError
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "class": "logging.Formatter",
                    "style": "{",
                    "datefmt": "%Y-%m-%d %H:%M",
                    "format": "[{asctime:s}] {message:s}\n",
                }
            },
            "handlers": {
                "default": {
                    "level": "DEBUG",
                    "class": "logging.handlers.WatchedFileHandler",
                    "formatter": "default",
                    "filename": logpath.as_posix(),
                    "mode": "w",
                    "encoding": "utf-8",
                }
            },
            "loggers": {"": {"handlers": ["default"], "level": "DEBUG", "propagate": False}},  # root logger
        }
    )
    return logpath


def cleanup_log(logpath: str = ""):
    """
    Delete the log file if it's empty
    """
    logpath = Path(logpath, "whispers.log")
    if not logpath.stat().st_size:
        remove(logpath.as_posix())


def debug(message: str = "") -> str:
    trace = traceback.format_exc().strip()
    if trace == "NoneType: None":
        ret = message
    else:
        ret = f"{trace}\n{message}"
    log = logging.getLogger()
    log.warning(ret)
    return ret
