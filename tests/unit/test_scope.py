import pytest

from tests.unit.conftest import FIXTURE_PATH, config_path, fixture_path
from whispers.core.args import parse_args
from whispers.core.config import load_config
from whispers.core.scope import load_scope


@pytest.mark.parametrize(
    ("src", "expected"),
    [(fixture_path("404"), 0), (fixture_path(".npmrc"), 1), (fixture_path(), len(list(FIXTURE_PATH.rglob("**/*")))),],
)
def test_load_scope(src, expected):
    args = parse_args([src])
    config = load_config(args)
    scope = load_scope(args, config)
    assert len(list(scope)) == expected


@pytest.mark.parametrize(
    ("config_file", "expected"), [("include_files.yml", [FIXTURE_PATH.joinpath(".pypirc")]), ("exclude_files.yml", [])],
)
def test_load_scope_config(config_file, expected):
    args = parse_args(["-c", config_path(config_file), fixture_path()])
    config = load_config(args)
    scope = load_scope(args, config)
    assert list(scope) == expected
