import pytest

from whispers.plugins import WhisperPlugins
from whispers.plugins.config import Config
from whispers.plugins.dockerfile import Dockerfile
from whispers.plugins.go import Go
from whispers.plugins.htpasswd import Htpasswd
from whispers.plugins.java import Java
from whispers.plugins.javascript import Javascript
from whispers.plugins.jproperties import Jproperties
from whispers.plugins.json import Json
from whispers.plugins.npmrc import Npmrc
from whispers.plugins.php import Php
from whispers.plugins.pip import Pip
from whispers.plugins.plaintext import Plaintext
from whispers.plugins.pypirc import Pypirc
from whispers.plugins.python import Python
from whispers.plugins.shell import Shell
from whispers.plugins.xml import Xml
from whispers.plugins.yml import Yml

from .conftest import fixture_path


@pytest.mark.parametrize(
    ("filename", "expected_plugin"),
    [
        ("File.404", type(None)),
        ("", type(None)),
        (".aws/credentials", Config),
        (".htpasswd", Htpasswd),
        (".npmrc", Npmrc),
        (".pypirc", Pypirc),
        ("apikeys.json", Json),
        ("apikeys.xml", Xml),
        ("apikeys.yml", Yml),
        ("connection.config", Xml),
        ("cors.py", Python),
        ("Dockerfile", Dockerfile),
        ("integration.conf", Xml),
        ("java.properties", Jproperties),
        ("pip.conf", Pip),
        ("plaintext.txt", Plaintext),
        ("settings.cfg", Config),
        ("settings.env", Config),
        ("settings.ini", Config),
        ("language.sh", Shell),
        ("language.py", Python),
        ("language.js", Javascript),
        ("language.java", Java),
        ("language.go", Go),
        ("language.php", Php),
    ],
)
def test_init(filename, expected_plugin):
    filename = fixture_path(filename)
    plugin = WhisperPlugins(filename).plugin
    assert isinstance(plugin, expected_plugin)
