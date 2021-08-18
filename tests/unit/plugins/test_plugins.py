import pytest

from tests.unit.conftest import fixture_path
from whispers.plugins import WhisperPlugins
from whispers.plugins.config import Config
from whispers.plugins.dockercfg import Dockercfg
from whispers.plugins.dockerfile import Dockerfile
from whispers.plugins.go import Go
from whispers.plugins.html import Html
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
from whispers.rules import WhisperRules


@pytest.mark.parametrize(
    ("filename", "expected_plugin"),
    [
        ("File.404", type(None)),
        ("", type(None)),
        (".htpasswd", Htpasswd),
        (".npmrc", Npmrc),
        (".pypirc", Pypirc),
        ("apikeys.json", Json),
        ("invalid.json", Json),
        ("apikeys.yml", Yml),
        ("cloudformation.yml", Yml),
        ("apikeys.xml", Xml),
        ("connection.config", Xml),
        ("integration.conf", Xml),
        ("Dockerfile", Dockerfile),
        (".dockercfg", Dockercfg),
        ("java.properties", Jproperties),
        ("pip.conf", Pip),
        ("plaintext.txt", Plaintext),
        (".aws/credentials", Config),
        ("settings.cfg", Config),
        ("settings.env", Config),
        ("settings.ini", Config),
        ("language.sh", Shell),
        ("language.py", Python),
        ("cors.py", Python),
        ("language.js", Javascript),
        ("language.java", Java),
        ("language.go", Go),
        ("language.php", Php),
        ("language.html", Html),
    ],
)
def test_init(filename, expected_plugin):
    filename = fixture_path(filename)
    plugin = WhisperPlugins(filename, WhisperRules()).plugin
    assert isinstance(plugin, expected_plugin)
