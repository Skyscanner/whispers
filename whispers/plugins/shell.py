import shlex
from pathlib import Path
from typing import Iterator, Tuple

from whispers.core.log import global_exception_handler
from whispers.core.utils import ESCAPED_CHARS, KeyValuePair, strip_string


class Shell:
    def pairs(self, filepath: Path) -> Iterator[KeyValuePair]:
        for cmdline, lineno in self.read_commands(filepath):
            try:
                cmd = shlex.split(cmdline)
            except Exception:
                global_exception_handler(filepath.as_posix(), cmdline)
                continue

            if not cmd:
                continue

            elif cmd[0].lower() == "curl":
                yield from self.curl(cmd)

            for item in cmd:
                if "=" in item and len(item.split("=")) == 2:
                    key, value = item.split("=")
                    yield KeyValuePair(key, value, keypath=[key], line=lineno)

    def read_commands(self, filepath: Path) -> Tuple[str, int]:
        ret = []
        for lineno, line in enumerate(filepath.open(), 1):
            line = line.strip()
            if line.startswith("#"):  # Comments
                line = line.lstrip("#").strip()
                line = line.translate(ESCAPED_CHARS)

            elif line.endswith("\\"):  # Multi-line commands
                ret.append(line[:-1])
                continue

            ret.append(line)
            yield " ".join(ret), lineno
            ret = []

    def curl(self, cmd) -> Iterator[KeyValuePair]:
        key = "password"
        indicators_combined = ["-u", "--user", "-U", "--proxy-user", "-E", "--cert"]
        indicators_single = ["--tlspassword", "--proxy-tlspassword"]
        indicators = indicators_combined + indicators_single
        for indicator in indicators:
            if indicator not in cmd:
                continue

            idx = cmd.index(indicator)
            if len(cmd) == idx + 1:
                continue  # End of command

            credentials = strip_string(cmd[idx + 1])
            if indicator in indicators_single:
                yield KeyValuePair(key, credentials, [key])

            else:
                if ":" not in credentials:
                    continue  # Password not specified

                yield KeyValuePair(key, credentials.split(":")[1], [key])
