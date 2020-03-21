import pytest
from   check_wheel_contents.util import comma_split, pymodule_basename

@pytest.mark.parametrize('filename,expected', [
    ('foo.py', 'foo'),
    ('FOO.PY', None),
    ('.py', None),
    ('py', None),
    ('not-an-identifier.py', 'not-an-identifier'),
    ('def.py', 'def'),
    ('extra.ext.py', 'extra.ext'),
    ('foo.cpython-38-x86_64-linux-gnu.so', 'foo'),
    ('graph.cpython-37m-darwin.so', 'graph'),
    ('foo.cp38-win_amd64.pyd', 'foo'),
    ('foo.cp38-win32.pyd', 'foo'),
    ('foo.so', 'foo'),
    ('foo.pyd', None),
    ('_ffi.abi3.so', '_ffi'),
])
def test_pymodule_basename(filename, expected):
    assert pymodule_basename(filename) == expected

@pytest.mark.parametrize('sin,lout', [
    ('', []),
    (' ', []),
    (',', []),
    (' , ', []),
    (' , , ', []),
    ('foo', ['foo']),
    ('foo,bar', ['foo', 'bar']),
    ('foo, bar', ['foo', 'bar']),
    ('foo ,bar', ['foo', 'bar']),
    (' foo , bar ', ['foo', 'bar']),
    (' foo , , bar ', ['foo', 'bar']),
    ('foo,,bar', ['foo', 'bar']),
    ('foo bar', ['foo bar']),
    (',foo', ['foo']),
    ('foo,', ['foo']),
])
def test_comma_split(sin, lout):
    assert comma_split(sin) == lout
