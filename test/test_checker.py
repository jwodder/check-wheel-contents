from   pathlib                      import Path
import attr
import pytest
from   check_wheel_contents.checker  import NO_CONFIG, WheelChecker
from   check_wheel_contents.checks   import Check
from   check_wheel_contents.config   import Configuration
from   check_wheel_contents.filetree import Directory, File

def test_defaults():
    checker = WheelChecker()
    assert attr.asdict(checker, recurse=False) == {
        "selected": set(Check),
        "toplevel": None,
        "pkgtree": None,
    }

@pytest.mark.parametrize('kwargs,cfg', [
    ({}, Configuration()),
    (
        {
            "configpath": "custom.cfg",
            "select": {Check.W001, Check.W002, Check.W003, Check.W004},
        },
        Configuration(
            select={Check.W001, Check.W002, Check.W003, Check.W004},
            ignore={Check.W001, Check.W002},
        ),
    ),
    (
        {"configpath": None},
        Configuration(select={Check.W001, Check.W002}),
    ),
    (
        {"configpath": None, "select": {Check.W003, Check.W004}},
        Configuration(select={Check.W003, Check.W004}),
    ),
    (
        {"configpath": NO_CONFIG},
        Configuration(),
    ),
    (
        {"toplevel": ["foo.py", "bar/"]},
        Configuration(toplevel=["foo.py", "bar"]),
    ),
    (
        {"package": (), "src_dir": ()},
        Configuration(),
    ),
    (
        {"package": ('bar/',)},
        Configuration(package_paths=[Path('bar')]),
    ),
    (
        {"src_dir": ('src/',)},
        Configuration(src_dirs=[Path('src')]),
    ),
    (
        {"package": ('foo.py', 'bar'), "src_dir": ('src',)},
        Configuration(
            package_paths=[Path('foo.py'), Path('bar')],
            src_dirs=[Path('src')],
        ),
    ),
    (
        {
            "package": ('foo.py', 'bar'),
            "src_dir": ('src',),
            "package_omit": ["__init__.py"],
        },
        Configuration(
            package_paths=[Path('foo.py'), Path('bar')],
            src_dirs=[Path('src')],
            package_omit=["__init__.py"],
        ),
    ),
])
def test_configure_options(fs, mocker, faking_path, kwargs, cfg):
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
    apply_mock = mocker.patch.object(checker, 'apply_config')
    checker.configure_options(**kwargs)
    apply_mock.assert_called_once_with(cfg)

def test_apply_config_calls(mocker):
    pkgtree = Directory(
        path=None,
        entries={"TOPLEVEL": Directory(path='TOPLEVEL/')},
    )
    cfg = mocker.Mock(
        **{
            "get_selected_checks.return_value": mocker.sentinel.SELECTED,
            "get_package_tree.return_value": pkgtree,
        },
    )
    cfg.toplevel = ["TOPLEVEL"]
    checker = WheelChecker()
    checker.apply_config(cfg)
    assert attr.asdict(checker, recurse=False) == {
        "selected": mocker.sentinel.SELECTED,
        "toplevel": ["TOPLEVEL"],
        "pkgtree": pkgtree,
    }

def test_apply_config_toplevel_pkgtree_mismatch_warning(capsys, mocker):
    pkgtree = Directory(
        path=None,
        entries={
            "foo.py": File(('foo.py'), None, None),
            "bar": Directory(path='bar/'),
        },
    )
    cfg = mocker.Mock(
        **{
            "get_selected_checks.return_value": mocker.sentinel.SELECTED,
            "get_package_tree.return_value": pkgtree,
        },
    )
    cfg.toplevel = ["bar.py", "foo"]
    checker = WheelChecker()
    checker.apply_config(cfg)
    assert attr.asdict(checker, recurse=False) == {
        "selected": mocker.sentinel.SELECTED,
        "toplevel": ["bar.py", "foo"],
        "pkgtree": pkgtree,
    }
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == (
        'Warning: --toplevel value does not match top level of --package/'
        '--src-dir file tree\n'
    )

@pytest.mark.parametrize('toplevel,pkgtree', [
    (None, None),
    (["foo.py", "bar"], None),
    (
        None,
        Directory(
            path=None,
            entries={
                "foo.py": File(('foo.py'), None, None),
                "bar": Directory(path='bar/'),
            },
        ),
    ),
    (
        ["foo.py", "bar"],
        Directory(
            path=None,
            entries={
                "foo.py": File(('foo.py'), None, None),
                "bar": Directory(path='bar/'),
            },
        ),
    ),
])
def test_apply_config_no_warning(capsys, mocker, toplevel, pkgtree):
    cfg = mocker.Mock(
        **{
            "get_selected_checks.return_value": mocker.sentinel.SELECTED,
            "get_package_tree.return_value": pkgtree,
        },
    )
    cfg.toplevel = toplevel
    checker = WheelChecker()
    checker.apply_config(cfg)
    assert attr.asdict(checker, recurse=False) == {
        "selected": mocker.sentinel.SELECTED,
        "toplevel": toplevel,
        "pkgtree": pkgtree,
    }
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == ''

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
    assert str(excinfo.value) == 'configpath must be None, str, or NO_CONFIG'

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
