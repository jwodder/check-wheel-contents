import json
from   operator                        import attrgetter
from   pathlib                         import Path
from   pyfakefs.fake_pathlib           import FakePath
import pytest
from   check_wheel_contents.configfile import ConfigDict
from   check_wheel_contents.errors     import UserInputError

DATA_DIR = Path(__file__).with_name('data')

# Path somehow gets monkeypatched during testing, so in order to have access
# to the original class we'll simply create an instance of it
PATH = object.__new__(Path)

@pytest.fixture
def faking_path(monkeypatch):
    # Monkeypatch Path.__eq__ so that pyfakefs FakePaths compare equal to real
    # pathlib.Paths
    # <https://github.com/jmcgeheeiv/pyfakefs/issues/478#issuecomment-487492775>
    def path_eq(self, other):
        Path = type(PATH)
        if isinstance(other, (Path, FakePath)):
            return str(self) == str(other)
        return super(Path, self).__eq__(other)
    monkeypatch.setattr(type(PATH), '__eq__', path_eq)

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
        cfg = None
    else:
        cfg = ConfigDict(configpath=path, data=data)
    assert ConfigDict.from_file(path) == cfg

def test_from_file_bad_tool_section():
    path = DATA_DIR / 'bad-tool-sect.toml'
    with pytest.raises(UserInputError) as excinfo:
        ConfigDict.from_file(path)
    assert str(excinfo.value) \
        == f'{path}: tool.check-wheel-contents: not a table'
