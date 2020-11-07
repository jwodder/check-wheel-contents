import pytest
from   check_wheel_contents.errors import WheelValidationError
from   check_wheel_contents.util   import comma_split, find_wheel_dirs, \
                                            is_data_dir, is_dist_info_dir, \
                                            is_stubs_dir, pymodule_basename

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
    ('.dist-info', False),
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
    ('.data', False),
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

@pytest.mark.parametrize('namelist,project,version,expected', [
    (
        [
            "foo.py",
            "foo-1.0.dist-info/WHEEL",
            "foo-1.0.dist-info/RECORD",
        ],
        "foo",
        "1.0",
        ("foo-1.0.dist-info", None),
    ),
    (
        [
            "foo.py",
            "foo-1.0.dist-info/WHEEL",
            "foo-1.0.dist-info/RECORD",
            "foo-1.0.data/scripts/bar",
        ],
        "foo",
        "1.0",
        ("foo-1.0.dist-info", "foo-1.0.data"),
    ),
    (
        [
            "foo.py",
            "FOO-1.0.0.dist-info/WHEEL",
            "FOO-1.0.0.dist-info/RECORD",
            "foo-1.data/scripts/bar",
        ],
        "foo",
        "1.0",
        ("FOO-1.0.0.dist-info", "foo-1.data"),
    ),
    (
        [
            "foo.py",
            "FOO-1.0_1.dist-info/WHEEL",
            "FOO-1.0_1.dist-info/RECORD",
        ],
        "foo",
        "1.0.post1",
        ("FOO-1.0_1.dist-info", None),
    ),
])
def test_find_wheel_dirs(namelist, project, version, expected):
    assert find_wheel_dirs(namelist, project, version) == expected

@pytest.mark.parametrize('namelist,project,version,msg', [
    (
        [
            "foo.py",
            "foo-1.0.dist/WHEEL",
        ],
        "foo",
        "1.0",
        'No .dist-info directory in wheel',
    ),
    (
        [
            "foo.py",
            "bar-1.0.dist-info/WHEEL",
        ],
        "foo",
        "1.0",
        "Project & version of wheel's .dist-info directory do not match wheel"
        " name: 'bar-1.0.dist-info'"
    ),
    (
        [
            "foo.py",
            "foo-2.0.dist-info/WHEEL",
        ],
        "foo",
        "1.0",
        "Project & version of wheel's .dist-info directory do not match wheel"
        " name: 'foo-2.0.dist-info'"
    ),
    (
        [
            "foo.py",
            "foo-1.0.dist-info/WHEEL",
            "bar-2.0.dist-info/RECORD",
        ],
        "foo",
        "1.0",
        'Wheel contains multiple .dist-info directories',
    ),
    (
        [
            "foo.py",
            "FOO-1.0.0.dist-info/WHEEL",
            "foo-1.dist-info/RECORD",
        ],
        "foo",
        "1.0",
        'Wheel contains multiple .dist-info directories',
    ),
    (
        ["foo.py", ".dist-info/WHEEL"],
        "foo",
        "1.0",
        'No .dist-info directory in wheel',
    ),
    (
        [
            "foo.py",
            "foo-1.0.dist-info/WHEEL",
            "foo-1.0.data/scripts/bar",
            "FOO-1.data/headers/foo.h",
        ],
        "foo",
        "1.0",
        'Wheel contains multiple .data directories',
    ),
    (
        [
            "foo.py",
            "foo-1.0.dist-info/WHEEL",
            "bar-1.0.data/scripts/bar",
        ],
        "foo",
        "1.0",
        "Project & version of wheel's .data directory do not match"
        " wheel name: 'bar-1.0.data'"
    ),
    (
        [
            "foo.py",
            "foo-1.0.dist-info/WHEEL",
            "foo-2.0.data/scripts/bar",
        ],
        "foo",
        "1.0",
        "Project & version of wheel's .data directory do not match"
        " wheel name: 'foo-2.0.data'"
    ),
])
def test_find_wheel_dirs_error(namelist, project, version, msg):
    with pytest.raises(WheelValidationError) as excinfo:
        find_wheel_dirs(namelist, project, version)
    assert str(excinfo.value) == msg
