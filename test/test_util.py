import pytest
from   check_wheel_contents.util import comma_split, is_data_dir, \
                                            is_dist_info_dir, is_stubs_dir, \
                                            pymodule_basename

@pytest.mark.parametrize('filename,expected', [
    ('foo.py', 'foo'),
    ('FOO.PY', None),
    ('foo.pyc', None),
    ('foo.pyo', None),
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
    ('foo.pyd', 'foo'),
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

@pytest.mark.parametrize('name,expected', [
    ('somepackage-1.0.0.dist-info', True),
    ('somepackage.dist-info', False),
    ('somepackage-1.0.0-1.dist-info', False),
    ('somepackage-1.0.0.data', False),
    ('SOME_._PaCkAgE-0.dist-info', True),
    ('foo-1!2+local.dist-info', True),
    ('foo-1_2_local.dist-info', True),
])
def test_is_dist_info_dir(name, expected):
    assert is_dist_info_dir(name) is expected

@pytest.mark.parametrize('name,expected', [
    ('somepackage-1.0.0.data', True),
    ('somepackage.data', False),
    ('somepackage-1.0.0-1.data', False),
    ('somepackage-1.0.0.dist-info', False),
    ('SOME_._PaCkAgE-0.data', True),
    ('foo-1!2+local.data', True),
    ('foo-1_2_local.data', True),
])
def test_is_data_dir(name, expected):
    assert is_data_dir(name) is expected

@pytest.mark.parametrize('name,expected', [
    ('foo-stubs', True),
    ('foo-stub', False),
    ('foo-STUBS', False),
    ('-stubs', False),
    ('def-stubs', False),
    ('has-hyphen-stubs', False),
    ('has.period-stubs', False),
])
def test_is_stubs_dir(name, expected):
    assert is_stubs_dir(name) is expected
