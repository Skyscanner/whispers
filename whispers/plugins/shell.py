import shlex
from pathlib import Path

from whispers.log import debug
from whispers.utils import escaped_chars, strip_string


class Shell:
    def pairs(self, filepath: Path):
        for cmdline in self.read_commands(filepath):
            try:
                cmd = shlex.split(cmdline)
            except Exception:
                debug(f"Failed parsing {filepath.as_posix()}\n{cmdline}")
                continue
            if not cmd:
                continue
            elif cmd[0].lower() == "curl":
                yield from self.curl(cmd)
            for item in cmd:
                if "=" in item and len(item.split("=")) == 2:
                    key, value = item.split("=")
                    yield key, value

    def read_commands(self, filepath: Path) -> str:
        ret = []
        for line in filepath.open("r").readlines():
            line = line.strip()
            if line.startswith("#"):  # Comments
                line = line.lstrip("#").strip()
                line = line.translate(escaped_chars)
            elif line.endswith("\\"):  # Multi-line commands
                ret.append(line[:-1])
                continue
            ret.append(line)
            yield " ".join(ret)
            ret = []

    def curl(self, cmd):
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
                yield "cURL_Password", credentials
            else:
                if ":" not in credentials:
                    continue  # Password not specified
                yield "cURL_Password", credentials.split(":")[1]
