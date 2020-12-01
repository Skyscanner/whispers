from datetime import datetime
from os import remove

import astroid
import pytest
from astroid.node_classes import AssignName, Const, JoinedStr, Name

from tests.unit.conftest import FIXTURE_PATH, does_not_raise
from whispers.plugins.python import Python


@pytest.mark.parametrize(
    ("code", "exception"),
    [
        ("a=1", does_not_raise()),
        ("invalid:", pytest.raises(StopIteration)),
    ],
)
def test_pairs(code, exception):
    stamp = datetime.now().timestamp()
    testfile = FIXTURE_PATH.joinpath(f"test-{stamp}.py")
    testfile.write_text(code)
    plugin = Python()
    with exception:
        try:
            next(plugin.pairs(testfile))
        except Exception:
            raise
        finally:
            remove(testfile.as_posix())


@pytest.mark.parametrize(
    ("key", "expectation"),
    [
        (None, False),
        (True, False),
        (1, False),
        ("a", False),
        (Name(), True),
        (AssignName(), True),
        (Const("a"), False),
        (JoinedStr("a"), False),
    ],
)
def test_is_key(key, expectation):
    plugin = Python()
    assert plugin.is_key(key) == expectation


@pytest.mark.parametrize(
    ("value", "expectation"),
    [
        (None, False),
        (True, False),
        (1, False),
        ("a", False),
        (Name(), False),
        (AssignName(), False),
        (Const("a"), True),
        (JoinedStr("a"), True),
    ],
)
def test_is_value(value, expectation):
    plugin = Python()
    assert plugin.is_value(value) == expectation


@pytest.mark.parametrize(
    ("code", "key", "value", "exception"),
    [
        ("a=1", "a", 1, does_not_raise()),
        ("a='b'", "a", "b", does_not_raise()),
        ("a=b", "", "", pytest.raises(StopIteration)),
        ("a==1", "a", 1, does_not_raise()),
        ("a=='b'", "a", "b", does_not_raise()),
        ("'b'==a", "a", "b", does_not_raise()),
        ("a==b", "", "", pytest.raises(StopIteration)),
        ("a==''", "", "", pytest.raises(StopIteration)),
        ("{'a': 1}", "a", 1, does_not_raise()),
        ("{'a': 'b'}", "a", "b", does_not_raise()),
        ("{'a': ''}", "", "", pytest.raises(StopIteration)),
    ],
)
def test_traverse_parse(code, key, value, exception):
    plugin = Python()
    ast = astroid.parse(code)
    pairs = plugin.traverse(ast)
    with exception:
        assert next(pairs) == (key, value)


@pytest.mark.parametrize(
    ("code", "key", "value", "exception"),
    [
        ("callback(a=1)", "a", 1, does_not_raise()),
        ("callback(a='b')", "a", "b", does_not_raise()),
        ("callback(a='')", "", "", pytest.raises(StopIteration)),
        ("a=os.getenv('b')", "function", "os.getenv('b')", does_not_raise()),
    ],
)
def test_traverse_extract(code, key, value, exception):
    plugin = Python()
    ast = astroid.extract_node(code)
    pairs = plugin.traverse(ast)
    with exception:
        assert next(pairs) == (key, value)
