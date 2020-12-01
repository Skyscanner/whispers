import pytest

from tests.unit.conftest import CONFIG_PATH, FIXTURE_PATH, config_path, fixture_path
from whispers import core
from whispers.cli import parse_args
from whispers.secrets import WhisperSecrets


@pytest.mark.parametrize("configfile", ["exclude_keys.yml", "exclude_values.yml"])
@pytest.mark.parametrize("src", ["excluded.yml", "excluded.json", "excluded.xml"])
def test_exclude_by_keys_and_values(configfile, src):
    args = parse_args([fixture_path(src)])
    args.config = core.load_config(config_path(configfile), FIXTURE_PATH)
    secrets = core.run(args)
    assert next(secrets).key == "hardcoded_password"
    with pytest.raises(StopIteration):
        next(secrets)


@pytest.mark.parametrize(
    ("src", "keys"),
    [
        ("privatekeys.yml", ["access", "key", "rsa", "dsa", "ec", "openssh"]),
        ("privatekeys.json", ["access", "key", "rsa", "dsa", "ec", "openssh"]),
        ("privatekeys.xml", ["access", "key", "rsa", "dsa", "ec", "openssh"]),
        ("aws.yml", ["aws_id", "aws_key", "aws_token"]),
        ("aws.json", ["aws_id", "aws_key", "aws_token"]),
        ("aws.xml", ["aws_id", "aws_key", "aws_token"]),
        ("jenkins.xml", ["noncompliantApiToken", "noncompliantPasswordHash"]),
        ("cloudformation.yml", ["NoncompliantDBPassword"]),
        ("cloudformation.json", ["NoncompliantDBPassword"]),
    ],
)
def test_detection_by_key(src, keys):
    args = parse_args([fixture_path(src)])
    secrets = core.run(args)
    for key in keys:
        assert next(secrets).key == key
    with pytest.raises(StopIteration):
        next(secrets)


@pytest.mark.parametrize(
    ("src", "count"),
    [
        ("custom.yml", 0),
        ("custom.json", 0),
        ("custom.xml", 0),
        ("hardcoded.yml", 5),
        ("hardcoded.json", 5),
        ("hardcoded.xml", 5),
        ("passwords.yml", 4),
        ("passwords.json", 4),
        ("passwords.xml", 4),
        ("placeholders.yml", 0),
        ("placeholders.json", 0),
        ("placeholders.xml", 0),
        ("apikeys.yml", 10),
        ("apikeys.json", 10),
        ("apikeys.xml", 10),
        (".npmrc", 3),
        (".pypirc", 1),
        ("pip.conf", 2),
        ("integration.conf", 5),
        ("integration.yml", 5),
        ("integration.json", 5),
        ("integration.xml", 5),
        ("settings.conf", 1),
        ("settings.cfg", 1),
        ("settings.ini", 1),
        ("settings.env", 1),
        ("Dockerfile", 3),
        ("beans.xml", 3),
        ("beans.xml.dist", 3),
        ("beans.xml.template", 3),
        ("jdbc.xml", 3),
        (".htpasswd", 2),
        (".aws/credentials", 3),
        ("falsepositive.yml", 4),
        ("language.sh", 14),
        ("language.py", 11),
        ("language.js", 4),
        ("language.java", 3),
        ("language.go", 9),
        ("language.php", 4),
        ("plaintext.txt", 2),
        ("uri.yml", 2),
        ("java.properties", 3),
        ("webhooks.yml", 3),
        ("creditcards.yml", 3),
    ],
)
def test_detection_by_value(src, count):
    args = parse_args([fixture_path(src)])
    args.config = core.load_config(CONFIG_PATH.joinpath("detection_by_value.yml"))
    secrets = core.run(args)
    for _ in range(count):
        value = next(secrets).value.lower()
        if value.isnumeric():
            continue
        assert "hardcoded" in value
    with pytest.raises(StopIteration):
        next(secrets)


def test_detection_by_filename():
    expected = map(
        fixture_path,
        [
            ".aws/credentials",
            ".htpasswd",
            ".npmrc",
            ".pypirc",
            "connection.config",
            "integration.conf",
            "pip.conf",
            "settings.cfg",
            "settings.conf",
            "settings.env",
            "settings.ini",
        ],
    )
    args = parse_args([fixture_path()])
    args.config = core.load_config(CONFIG_PATH.joinpath("detection_by_filename.yml"))
    secrets = core.run(args)
    result = [secret.value for secret in secrets]
    for exp in expected:
        assert exp in result


@pytest.mark.parametrize(
    ("key", "value", "expectation"),
    [
        (None, None, False),
        ("", "", False),
        ("", "$value", False),
        ("", "{{value}}", False),
        ("", "{value}", False),
        ("", "{whispers~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~}", False),
        ("", "{d2hpc3BlcnN+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+}", True),
        ("", "${value$}", False),
        ("", "<value>", False),
        ("", "{value}", False),
        ("", "null", False),
        ("", "!Ref Value", False),
        ("", "{value}", False),
        ("", "/path/value", False),
        ("whispers", "WHISPERS", False),
        ("label", "WhispersLabel", False),
        ("SECRET_VALUE_KEY", "whispers", False),
        ("whispers", "SECRET_VALUE_PLACEHOLDER", False),
        ("secret", "whispers", True),
    ],
)
def test_is_static(key, value, expectation):
    args = parse_args([fixture_path()])
    args.config = core.load_config(CONFIG_PATH.joinpath("example.yml"))
    secrets = WhisperSecrets(args)
    assert secrets.is_static(key, value) == expectation
