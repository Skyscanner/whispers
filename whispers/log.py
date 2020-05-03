import logging
import logging.config
import traceback
from pathlib import Path


def configure_log(path: str = ""):
    path = Path(path, "whispers.log")
    path.write_text("")
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
                    "filename": path.as_posix(),
                    "mode": "w",
                    "encoding": "utf-8",
                }
            },
            "loggers": {"": {"handlers": ["default"], "level": "DEBUG", "propagate": False}},  # root logger
        }
    )


def debug(message: str = "") -> str:
    trace = traceback.format_exc().strip()
    if trace == "NoneType: None":
        ret = message
    else:
        ret = f"{trace}\n{message}"
    log = logging.getLogger()
    log.warning(ret)
    return ret
