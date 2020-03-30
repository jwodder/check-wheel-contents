import attr
import pytest
from   check_wheel_contents.checker  import WheelChecker
from   check_wheel_contents.checks   import Check
from   check_wheel_contents.filetree import Directory, File

def test_defaults():
    checker = WheelChecker()
    assert attr.asdict(checker, retain_collection_types=True) == {
        "selected": set(Check),
        "toplevel": None,
        "pkgtree": None,
    }

@pytest.mark.parametrize('kwargs,expected', [
    ({}, WheelChecker()),
    (
        {
            "configpath": "custom.cfg",
            "select": {Check.W001, Check.W002, Check.W003, Check.W004},
        },
        WheelChecker(selected={Check.W003, Check.W004})
    ),
    (
        {"configpath": None},
        WheelChecker(selected={Check.W001, Check.W002})
    ),
    (
        {"toplevel": ["foo.py", "bar/"]},
        WheelChecker(toplevel=["foo.py", "bar"]),
    ),
    (
        {"package": (), "src_dir": ()},
        WheelChecker(),
    ),
    (
        {"package": ('bar/',)},
        WheelChecker(
            pkgtree=Directory(
                path=None,
                entries={
                    "bar": Directory(
                        path="bar/",
                        entries={
                            "__init__.py": File(('bar', '__init__.py'), None, None),
                            "bar.py": File(('bar', 'bar.py'), None, None),
                        },
                    ),
                },
            ),
        ),
    ),
    (
        {"src_dir": ('src/',)},
        WheelChecker(
            pkgtree=Directory(
                path=None,
                entries={
                    "quux": Directory(
                        path="quux/",
                        entries={
                            "__init__.py": File(('quux', '__init__.py'), None, None),
                            "quux.py": File(('quux', 'quux.py'), None, None),
                        },
                    ),
                },
            ),
        ),
    ),
    (
        {"package": ('foo.py', 'bar'), "src_dir": ('src',)},
        WheelChecker(
            pkgtree=Directory(
                path=None,
                entries={
                    "foo.py": File(('foo.py',), None, None),
                    "bar": Directory(
                        path="bar/",
                        entries={
                            "__init__.py": File(('bar', '__init__.py'), None, None),
                            "bar.py": File(('bar', 'bar.py'), None, None),
                        },
                    ),
                    "quux": Directory(
                        path="quux/",
                        entries={
                            "__init__.py": File(('quux', '__init__.py'), None, None),
                            "quux.py": File(('quux', 'quux.py'), None, None),
                        },
                    ),
                },
            ),
        ),
    ),
])
def test_configure_options(fs, kwargs, expected):
    fs.create_file('/usr/src/project/foo.py')
    fs.create_file('/usr/src/project/bar/__init__.py')
    fs.create_file('/usr/src/project/bar/bar.py')
    fs.create_file('/usr/src/project/src/quux/__init__.py')
    fs.create_file('/usr/src/project/src/quux/quux.py')
    fs.create_file(
        '/usr/src/project/check-wheel-contents.cfg',
        contents=(
            '[check-wheel-contents]\n'
            'select = W001,W002\n'
        ),
    )
    fs.create_file(
        '/usr/src/project/custom.cfg',
        contents=(
            '[check-wheel-contents]\n'
            'ignore = W001,W002\n'
        ),
    )
    fs.cwd = '/usr/src/project'
    checker = WheelChecker()
    checker.configure_options(**kwargs)
    assert checker == expected

@pytest.mark.parametrize('value', [
    42,
    ['foo.py'],
    ('foo.py',),
    [None],
])
def test_configure_options_error(value):
    checker = WheelChecker()
    with pytest.raises(TypeError) as excinfo:
        checker.configure_options(configpath=value)
    assert str(excinfo.value) == 'configpath must be None, str, or attr.NOTHING'

def test_check_contents(mocker):
    checker = WheelChecker()
    check_mocks = {}
    for c in Check:
        check_mocks[c] = mocker.patch.object(
            checker,
            'check_' + c.name,
            return_value=[getattr(mocker.sentinel, c.name)],
        )
    checker.selected = {Check.W001, Check.W002, Check.W003, Check.W005}
    assert checker.check_contents(mocker.sentinel.CONTENTS) == [
        mocker.sentinel.W001,
        mocker.sentinel.W002,
        mocker.sentinel.W003,
        mocker.sentinel.W005,
    ]
    for c,m in check_mocks.items():
        if c in checker.selected:
            m.assert_called_once_with(mocker.sentinel.CONTENTS)
        else:
            m.assert_not_called()
