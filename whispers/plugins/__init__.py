from pathlib import Path

from whispers.plugins.config import Config
from whispers.plugins.dockerfile import Dockerfile
from whispers.plugins.htpasswd import Htpasswd
from whispers.plugins.jproperties import Jproperties
from whispers.plugins.json import Json
from whispers.plugins.npmrc import Npmrc
from whispers.plugins.pip import Pip
from whispers.plugins.plaintext import Plaintext
from whispers.plugins.pypirc import Pypirc
from whispers.plugins.python import Python
from whispers.plugins.shell import Shell
from whispers.plugins.xml import Xml
from whispers.plugins.yml import Yml


class WhisperPlugins:
    def __init__(self, filename: str):
        """Inits the correct plugin for a given filename"""
        self.filename = filename
        self.filepath = Path(filename)
        self.filetype = self.filepath.name.split(".")[-1]
        self.plugin = None
        if not self.filepath.exists():
            self.plugin = None
        elif not self.filepath.is_file():
            self.plugin = None
        elif self.filepath.stat().st_size < 7:
            self.plugin = None
        elif self.filetype in ["yaml", "yml"]:
            self.plugin = Yml()
        elif self.filetype == "json":
            self.plugin = Json()
        elif self.filetype == "xml":
            self.plugin = Xml()
        elif self.filetype.startswith("npmrc"):
            self.plugin = Npmrc()
        elif self.filetype.startswith("pypirc"):
            self.plugin = Pypirc()
        elif self.filepath.name == "pip.conf":
            self.plugin = Pip()
        elif self.filetype in ["conf", "cfg", "config", "ini", "env", "credentials"]:
            if self.filepath.open("r").readline().startswith("<?xml "):
                self.plugin = Xml()
            else:
                self.plugin = Config()
        elif self.filetype == "properties":
            self.plugin = Jproperties()
        elif self.filetype.startswith(("sh", "bash", "zsh", "env")):
            self.plugin = Shell()
        elif self.filepath.name.startswith("Dockerfile"):
            self.plugin = Dockerfile()
        elif self.filetype.startswith("htpasswd"):
            self.plugin = Htpasswd()
        elif self.filetype == "txt":
            self.plugin = Plaintext()
        elif self.filetype == "py":
            self.plugin = Python()

    def pairs(self):
        if self.plugin:
            yield from self.plugin.pairs(self.filepath)
