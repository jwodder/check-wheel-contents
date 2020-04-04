import json
from   operator                    import attrgetter
from   pathlib                     import Path
import pytest
from   check_wheel_contents.checks import Check
from   check_wheel_contents.config import ConfigDict
from   check_wheel_contents.errors import UserInputError

DATA_DIR = Path(__file__).with_name('data')

@pytest.mark.parametrize('files,cfgdict', [
    (
        {
            '/usr/src/project/pyproject.toml':
                '[tool.check-wheel-contents]\n'
                'select = "W001"\n',
            '/usr/src/project/tox.ini':
                '[check-wheel-contents]\n'
                'select = W002\n',
            '/usr/src/project/setup.cfg':
                '[tool:check-wheel-contents]\n'
                'select = W003\n',
            '/usr/src/project/check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W004\n',
            '/usr/src/project/.check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W005\n',
        },
        ConfigDict(
            configpath=Path('pyproject.toml'),
            data={"select": "W001"},
        ),
    ),

    (
        {
            '/usr/src/project/pyproject.toml': '',
            '/usr/src/project/tox.ini':
                '[check-wheel-contents]\n'
                'select = W002\n',
            '/usr/src/project/setup.cfg':
                '[tool:check-wheel-contents]\n'
                'select = W003\n',
            '/usr/src/project/check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W004\n',
            '/usr/src/project/.check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W005\n',
        },
        ConfigDict(
            configpath=Path('tox.ini'),
            data={"select": "W002"},
        ),
    ),

    (
        {
            '/usr/src/project/tox.ini':
                '[check-wheel-contents]\n'
                'select = W002\n',
            '/usr/src/project/setup.cfg':
                '[tool:check-wheel-contents]\n'
                'select = W003\n',
            '/usr/src/project/check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W004\n',
            '/usr/src/project/.check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W005\n',
        },
        ConfigDict(
            configpath=Path('tox.ini'),
            data={"select": "W002"},
        ),
    ),

    (
        {
            '/usr/src/project/tox.ini': '',
            '/usr/src/project/setup.cfg':
                '[tool:check-wheel-contents]\n'
                'select = W003\n',
            '/usr/src/project/check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W004\n',
            '/usr/src/project/.check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W005\n',
        },
        ConfigDict(
            configpath=Path('setup.cfg'),
            data={"select": "W003"},
        ),
    ),

    (
        {
            '/usr/src/project/setup.cfg':
                '[tool:check-wheel-contents]\n'
                'select = W003\n',
            '/usr/src/project/check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W004\n',
            '/usr/src/project/.check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W005\n',
        },
        ConfigDict(
            configpath=Path('setup.cfg'),
            data={"select": "W003"},
        ),
    ),

    (
        {
            '/usr/src/project/setup.cfg': '',
            '/usr/src/project/check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W004\n',
            '/usr/src/project/.check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W005\n',
        },
        ConfigDict(
            configpath=Path('check-wheel-contents.cfg'),
            data={"select": "W004"},
        ),
    ),

    (
        {
            '/usr/src/project/check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W004\n',
            '/usr/src/project/.check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W005\n',
        },
        ConfigDict(
            configpath=Path('check-wheel-contents.cfg'),
            data={"select": "W004"},
        ),
    ),

    (
        {
            '/usr/src/project/check-wheel-contents.cfg': '',
            '/usr/src/project/.check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W005\n',
        },
        ConfigDict(
            configpath=Path('.check-wheel-contents.cfg'),
            data={"select": "W005"},
        ),
    ),

    (
        {
            '/usr/src/project/.check-wheel-contents.cfg':
                '[check-wheel-contents]\n'
                'select = W005\n',
        },
        ConfigDict(
            configpath=Path('.check-wheel-contents.cfg'),
            data={"select": "W005"},
        ),
    ),

    (
        {'/usr/src/project/.check-wheel-contents.cfg': ''},
        None,
    ),

    ({}, None),

    (
        {
            "/usr/src/tox.ini":
                '[check-wheel-contents]\n'
                'select = W002\n',
            "/usr/src/project/setup.cfg":
                '[tool:check-wheel-contents]\n'
                'select = W003\n',
        },
        ConfigDict(
            configpath=Path('setup.cfg'),
            data={"select": "W003"},
        ),
    ),

    (
        {
            "/usr/src/tox.ini":
                '[check-wheel-contents]\n'
                'select = W002\n',
            "/usr/src/project/setup.cfg": '',
        },
        None,
    ),

    (
        {
            "/usr/src/tox.ini":
                '[check-wheel-contents]\n'
                'select = W002\n',
        },
        ConfigDict(
            configpath=Path('/usr/src/tox.ini'),
            data={"select": "W002"},
        ),
    ),

    (
        {
            "/usr/src/tox.ini":
                '[check-wheel-contents]\n'
                'select = W002\n',
            "/usr/pyproject.toml":
                '[tool.check-wheel-contents]\n'
                'select = "W001"\n',
        },
        ConfigDict(
            configpath=Path('/usr/src/tox.ini'),
            data={"select": "W002"},
        ),
    ),

    (
        {
            "/usr/src/tox.ini": '',
            "/usr/pyproject.toml":
                '[tool.check-wheel-contents]\n'
                'select = "W001"\n',
        },
        None,
    ),

    (
        {
            "/usr/pyproject.toml":
                '[tool.check-wheel-contents]\n'
                'select = "W001"\n',
        },
        ConfigDict(
            configpath=Path('/usr/pyproject.toml'),
            data={"select": "W001"},
        ),
    ),

    (
        {
            "/usr/src/setup.cfg":
                '[tool:check-wheel-contents]\n'
                'select = W003\n',
        },
        ConfigDict(
            configpath=Path('/usr/src/setup.cfg'),
            data={"select": "W003"},
        ),
    )
])
def test_find_default(fs, files, cfgdict, faking_path):
    for path, text in files.items():
        fs.create_file(path, contents=text)
    fs.cwd = '/usr/src/project'
    assert ConfigDict.find_default() == cfgdict

@pytest.mark.parametrize('path', [
    p for p in (DATA_DIR / 'configfiles').iterdir()
      if p.suffix != '.json'
], ids=attrgetter("name"))
def test_from_file(path):
    datafile = path.with_suffix('.json')
    try:
        data = json.loads(datafile.read_text())
    except FileNotFoundError:
        cfgdict = None
    else:
        cfgdict = ConfigDict(configpath=path, data=data)
    assert ConfigDict.from_file(path) == cfgdict

def test_from_file_bad_tool_section():
    path = DATA_DIR / 'bad-tool-sect.toml'
    with pytest.raises(UserInputError) as excinfo:
        ConfigDict.from_file(path)
    assert str(excinfo.value) \
        == f'{path}: tool.check-wheel-contents: not a table'

@pytest.mark.parametrize('data,expected', [
    ({}, None),
    ({"key": ""}, []),
    ({"key": "foo"}, ["foo"]),
    ({"key": "foo, bar,"}, ["foo", "bar"]),
    ({"key": ["foo", "bar"]}, ["foo", "bar"]),
    ({"key": ["foo, bar,"]}, ["foo, bar,"]),
])
def test_get_comma_list(data, expected):
    cfgdict = ConfigDict(configpath=Path('foo.cfg'), data=data)
    assert cfgdict.get_comma_list("key") == expected

@pytest.mark.parametrize('value', [
    None,
    42,
    True,
    [42],
    ["foo", 42],
    ["foo", None],
])
def test_get_comma_list_error(value):
    cfgdict = ConfigDict(configpath=Path('foo.cfg'), data={"key": value})
    with pytest.raises(UserInputError) as excinfo:
        cfgdict.get_comma_list("key")
    assert str(excinfo.value) \
        == 'foo.cfg: key: value must be comma-separated string or list of strings'

@pytest.mark.parametrize('data,expected', [
    ({}, None),
    ({"key": ""}, set()),
    ({"key": "W001"}, {Check.W001}),
    ({"key": "W001, W002,"}, {Check.W001, Check.W002}),
    ({"key": ["W001", "W002"]}, {Check.W001, Check.W002}),
])
def test_get_check_set(data, expected):
    cfgdict = ConfigDict(configpath=Path('foo.cfg'), data=data)
    assert cfgdict.get_check_set("key") == expected

@pytest.mark.parametrize('value,badbit', [
    (["W001, W002,"], "W001, W002,"),
    (["W", ""], ""),
    (["W9", ""], "W9"),
])
def test_get_check_set_value_error(value, badbit):
    cfgdict = ConfigDict(configpath=Path('foo.cfg'), data={"key": value})
    with pytest.raises(UserInputError) as excinfo:
        cfgdict.get_check_set("key")
    assert str(excinfo.value) \
        == f'foo.cfg: key: Unknown/invalid check prefix: {badbit!r}'

@pytest.mark.parametrize('value', [
    None,
    42,
    True,
    [42],
    ["foo", 42],
    ["foo", None],
])
def test_get_check_set_type_error(value):
    cfgdict = ConfigDict(configpath=Path('foo.cfg'), data={"key": value})
    with pytest.raises(UserInputError) as excinfo:
        cfgdict.get_check_set("key")
    assert str(excinfo.value) \
        == 'foo.cfg: key: value must be comma-separated string or list of strings'

BASE = Path('/usr/src/project/path')

@pytest.mark.parametrize('data,expected', [
    ({}, None),
    ({"key": ""}, []),
    ({"key": "foo"}, [BASE / 'foo']),
    (
        {"key": "foo, bar/, test/data, /usr/src"},
        [BASE / 'foo', BASE / 'bar', BASE / 'test' / 'data', Path('/usr/src')],
    ),
    (
        {"key": ["foo", "bar,baz", "test/data", "/usr/src"]},
        [BASE / 'foo', BASE / 'bar,baz', BASE / 'test' / 'data', Path('/usr/src')],
    ),
])
def test_get_path_list(fs, faking_path, data, expected):
    fs.create_file('/usr/src/project/path/foo')
    fs.create_file('/usr/src/project/path/bar')
    fs.create_file('/usr/src/project/path/bar,baz')
    fs.create_file('/usr/src/project/path/test/data')
    fs.cwd = '/usr/src/project'
    cfgdict = ConfigDict(configpath=Path('path/foo.cfg'), data=data)
    assert cfgdict.get_path_list("key") == expected

@pytest.mark.parametrize('value', [
    None,
    42,
    True,
    [42],
    ["foo", 42],
    ["foo", None],
])
def test_get_path_list_error(value):
    cfgdict = ConfigDict(configpath=Path('path/foo.cfg'), data={"key": value})
    with pytest.raises(UserInputError) as excinfo:
        cfgdict.get_path_list("key")
    assert str(excinfo.value) \
        == 'path/foo.cfg: key: value must be comma-separated string or list of strings'

def test_get_path_list_nonexistent(fs):
    fs.create_file('/usr/src/project/path/foo')
    fs.create_file('/usr/src/project/path/bar')
    fs.cwd = '/usr/src/project'
    cfgdict = ConfigDict(
        configpath=Path('path/foo.cfg'),
        data={"key": "foo,bar,quux"},
    )
    with pytest.raises(UserInputError) as excinfo:
        cfgdict.get_path_list("key")
    assert str(excinfo.value) \
        == "path/foo.cfg: key: no such file or directory: '/usr/src/project/path/quux'"

def test_get_path_list_require_dir_not_a_dir(fs):
    fs.create_file('/usr/src/project/path/foo')
    fs.create_file('/usr/src/project/path/bar')
    fs.cwd = '/usr/src/project'
    cfgdict = ConfigDict(
        configpath=Path('path/foo.cfg'),
        data={"key": "foo,bar,quux"},
    )
    with pytest.raises(UserInputError) as excinfo:
        cfgdict.get_path_list("key", require_dir=True)
    assert str(excinfo.value) \
        == "path/foo.cfg: key: not a directory: '/usr/src/project/path/foo'"
