import shlex
from pathlib import Path

from whispers.utils import escaped_chars, strip_string


class Shell:
    def pairs(self, filepath: Path):
        full_command = []
        for line in filepath.open("r").readlines():
            line = line.strip()
            if line.startswith("#"):  # Comments
                line = line.lstrip("#").strip()
                line = line.translate(escaped_chars)
            if line.endswith("\\"):  # Multi-line commands
                full_command.append(line[:-1])
                continue
            full_command.append(line)
            cmd = shlex.split(" ".join(full_command))
            full_command = []
            if not cmd:
                continue
            elif cmd[0].lower() == "curl":
                yield from self.curl(cmd)
            for item in cmd:
                if "=" in item and len(item.split("=")) == 2:
                    key, value = item.split("=")
                    yield key, value

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
