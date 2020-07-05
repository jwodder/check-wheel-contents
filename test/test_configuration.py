from   pathlib                     import Path
from   unittest.mock               import sentinel
import attr
import pytest
from   check_wheel_contents.checks   import Check
from   check_wheel_contents.config   import ConfigDict, Configuration, \
                                                TRAVERSAL_EXCLUSIONS
from   check_wheel_contents.errors   import UserInputError
from   check_wheel_contents.filetree import Directory, File

PROJECT_TREE = Path(__file__).with_name('data') / 'project-tree'

@pytest.mark.parametrize('toplevel_in,toplevel_out', [
    (None, None),
    (['foo.py', 'bar'], ['foo.py', 'bar']),
    (['foo.py', 'bar/'], ['foo.py', 'bar']),
])
@pytest.mark.parametrize('package_in,package_out', [
    ((), None),
    (('foo.py', 'bar'), [Path('foo.py'), Path('bar')]),
])
@pytest.mark.parametrize('src_dir_in,src_dir_out', [
    ((), None),
    (('quux',), [Path('quux')]),
])
@pytest.mark.parametrize('package_omit_in,package_omit_out', [
    (None, None),
    ([], []),
    (['RCS', '*.pyc'], ['RCS', '*.pyc']),
])
def test_from_command_options(toplevel_in, toplevel_out, package_in,
                              package_out, src_dir_in, src_dir_out,
                              package_omit_in, package_omit_out):
    cfg = Configuration.from_command_options(
        select = sentinel.SELECT,
        ignore = sentinel.IGNORE,
        toplevel = toplevel_in,
        package = package_in,
        src_dir = src_dir_in,
        package_omit = package_omit_in,
    )
    assert attr.asdict(cfg, recurse=False) == {
        "select": sentinel.SELECT,
        "ignore": sentinel.IGNORE,
        "toplevel": toplevel_out,
        "package_paths": package_out,
        "src_dirs": src_dir_out,
        "package_omit": package_omit_out,
    }

def test_from_command_options_default():
    cfg = Configuration.from_command_options()
    assert attr.asdict(cfg, recurse=False) == {
        "select": None,
        "ignore": None,
        "toplevel": None,
        "package_paths": None,
        "src_dirs": None,
        "package_omit": None,
    }

def test_from_config_dict_calls(mocker):
    cd = mocker.Mock(
        **{
            "get_comma_list.return_value": ["foo.py", "bar/"],
            "get_check_set.return_value": sentinel.CHECK_SET,
            "get_path_list.return_value": sentinel.PATH_LIST,
        },
    )
    cfg = Configuration.from_config_dict(cd)
    assert attr.asdict(cfg, recurse=False) == {
        "select": sentinel.CHECK_SET,
        "ignore": sentinel.CHECK_SET,
        "toplevel": ["foo.py", "bar"],
        "package_paths": sentinel.PATH_LIST,
        "src_dirs": sentinel.PATH_LIST,
        "package_omit": ["foo.py", "bar/"],
    }
    assert cd.get_check_set.call_count == 2
    cd.get_check_set.assert_any_call("select")
    cd.get_check_set.assert_any_call("ignore")
    assert cd.get_comma_list.call_count == 2
    cd.get_comma_list.assert_any_call("toplevel")
    cd.get_comma_list.assert_any_call("package_omit")
    assert cd.get_path_list.call_count == 2
    cd.get_path_list.assert_any_call("package")
    cd.get_path_list.assert_any_call("src_dir", require_dir=True)

@pytest.mark.parametrize('cfgdict,expected', [
    (
        ConfigDict(configpath=Path('foo.cfg'), data={}),
        Configuration(
            select = None,
            ignore = None,
            toplevel = None,
            package_paths = None,
            src_dirs = None,
            package_omit = None,
        ),
    ),
    (
        ConfigDict(
            configpath=PROJECT_TREE / 'cfg.ini',
            data={
                "select": "W001,W002",
                "ignore": "W003,W004",
                "toplevel": "foo.py,quux/",
                "package": "bar",
                "src_dir": "src",
                "package_omit": "__pycache__,test/data",
            },
        ),
        Configuration(
            select = {Check.W001, Check.W002},
            ignore = {Check.W003, Check.W004},
            toplevel = ["foo.py", "quux"],
            package_paths = [PROJECT_TREE / 'bar'],
            src_dirs = [PROJECT_TREE / 'src'],
            package_omit = ["__pycache__", "test/data"],
        ),
    ),
    (
        ConfigDict(
            configpath=PROJECT_TREE / 'cfg.ini',
            data={
                "select": ["W001", "W002"],
                "ignore": ["W003", "W004"],
                "toplevel": ["foo.py", "quux/"],
                "package": ["bar"],
                "src_dir": ["src"],
                "package_omit": ["__pycache__", "test/data"],
            },
        ),
        Configuration(
            select = {Check.W001, Check.W002},
            ignore = {Check.W003, Check.W004},
            toplevel = ["foo.py", "quux"],
            package_paths = [PROJECT_TREE / 'bar'],
            src_dirs = [PROJECT_TREE / 'src'],
            package_omit = ["__pycache__", "test/data"],
        ),
    ),
    (
        ConfigDict(
            configpath=Path('/usr/src/project/cfg.ini'),
            data={
                "toplevel": "",
                "package": "",
                "src_dir": "",
                "package_omit": "",
            },
        ),
        Configuration(
            select = None,
            ignore = None,
            toplevel = [],
            package_paths = [],
            src_dirs = [],
            package_omit = [],
        ),
    ),
    (
        ConfigDict(
            configpath=Path('/usr/src/project/cfg.ini'),
            data={
                "toplevel": [],
                "package": [],
                "src_dir": [],
                "package_omit": [],
            },
        ),
        Configuration(
            select = None,
            ignore = None,
            toplevel = [],
            package_paths = [],
            src_dirs = [],
            package_omit = [],
        ),
    ),
])
def test_from_config_dict(cfgdict, expected):
    assert Configuration.from_config_dict(cfgdict) == expected

@pytest.mark.parametrize('cfgdict', [
    None,
    ConfigDict(
        configpath=PROJECT_TREE / 'cfg.ini',
        data={
            "select": "W001,W002",
            "ignore": "W003,W004",
            "toplevel": "foo.py,quux/",
            "package": "bar",
            "src_dir": "src",
        },
    ),
])
def test_from_config_file(mocker, cfgdict):
    cdmock = mocker.patch('check_wheel_contents.config.ConfigDict', autospec=True)
    cdmock.from_file.return_value = cfgdict
    if cfgdict is None:
        expected = Configuration()
    else:
        expected = Configuration.from_config_dict(cfgdict)
    path = '/foo/bar/quux'
    cfg = Configuration.from_config_file(path)
    assert cfg == expected
    assert cdmock.method_calls == [mocker.call.from_file(Path(path))]

@pytest.mark.parametrize('cfgdict', [
    None,
    ConfigDict(
        configpath=PROJECT_TREE / 'cfg.ini',
        data={
            "select": "W001,W002",
            "ignore": "W003,W004",
            "toplevel": "foo.py,quux/",
            "package": "bar",
            "src_dir": "src",
        },
    ),
])
def test_from_config_file_none_path(mocker, cfgdict):
    cdmock = mocker.patch('check_wheel_contents.config.ConfigDict', autospec=True)
    cdmock.find_default.return_value = cfgdict
    if cfgdict is None:
        expected = Configuration()
    else:
        expected = Configuration.from_config_dict(cfgdict)
    cfg = Configuration.from_config_file(None)
    assert cfg == expected
    assert cdmock.method_calls == [mocker.call.find_default()]

@pytest.mark.parametrize('cfgdict', [
    None,
    ConfigDict(
        configpath=PROJECT_TREE / 'cfg.ini',
        data={
            "select": "W001,W002",
            "ignore": "W003,W004",
            "toplevel": "foo.py,quux/",
            "package": "bar",
            "src_dir": "src",
        },
    ),
])
def test_from_config_file_no_arg(mocker, cfgdict):
    cdmock = mocker.patch('check_wheel_contents.config.ConfigDict', autospec=True)
    cdmock.find_default.return_value = cfgdict
    if cfgdict is None:
        expected = Configuration()
    else:
        expected = Configuration.from_config_dict(cfgdict)
    cfg = Configuration.from_config_file()
    assert cfg == expected
    assert cdmock.method_calls == [mocker.call.find_default()]

@pytest.mark.parametrize('left,right,expected', [
    (Configuration(), Configuration(), Configuration()),
    (
        Configuration(
            select={Check.W001, Check.W002},
            ignore={Check.W003, Check.W004},
            toplevel=['foo.py', 'bar'],
            package_paths=[Path('foobar')],
            src_dirs=[Path('src')],
            package_omit=['__pycache__', 'RCS'],
        ),
        Configuration(
            select={Check.W005, Check.W006},
            ignore={Check.W007, Check.W008},
            toplevel=["quux", "glarch.py"],
            package_paths=[Path('baz.py')],
            src_dirs=[Path('source')],
            package_omit=['*.pyc', 'CVS'],
        ),
        Configuration(
            select={Check.W005, Check.W006},
            ignore={Check.W007, Check.W008},
            toplevel=["quux", "glarch.py"],
            package_paths=[Path('baz.py')],
            src_dirs=[Path('source')],
            package_omit=['*.pyc', 'CVS'],
        ),
    ),
    (
        Configuration(
            select={Check.W001, Check.W002},
            ignore={Check.W003, Check.W004},
            toplevel=['foo.py', 'bar'],
            package_paths=[Path('foobar')],
            src_dirs=[Path('src')],
            package_omit=['__pycache__', 'RCS'],
        ),
        Configuration(
            select={},
            ignore={},
            toplevel=[],
            package_paths=[],
            src_dirs=[],
            package_omit=[],
        ),
        Configuration(
            select={},
            ignore={},
            toplevel=[],
            package_paths=[],
            src_dirs=[],
            package_omit=[],
        ),
    ),
    (
        Configuration(
            select={Check.W001, Check.W002},
            ignore={Check.W003, Check.W004},
            toplevel=['foo.py', 'bar'],
            package_paths=[Path('foobar')],
            src_dirs=[Path('src')],
            package_omit=['__pycache__', 'RCS'],
        ),
        Configuration(
            select=None,
            ignore=None,
            toplevel=None,
            package_paths=None,
            src_dirs=None,
            package_omit=None,
        ),
        Configuration(
            select={Check.W001, Check.W002},
            ignore={Check.W003, Check.W004},
            toplevel=['foo.py', 'bar'],
            package_paths=[Path('foobar')],
            src_dirs=[Path('src')],
            package_omit=['__pycache__', 'RCS'],
        ),
    ),
    (
        Configuration(
            select=None,
            ignore=None,
            toplevel=None,
            package_paths=None,
            src_dirs=None,
            package_omit=None,
        ),
        Configuration(
            select={Check.W005, Check.W006},
            ignore={Check.W007, Check.W008},
            toplevel=["quux", "glarch.py"],
            package_paths=[Path('baz.py')],
            src_dirs=[Path('source')],
            package_omit=['__pycache__', 'RCS'],
        ),
        Configuration(
            select={Check.W005, Check.W006},
            ignore={Check.W007, Check.W008},
            toplevel=["quux", "glarch.py"],
            package_paths=[Path('baz.py')],
            src_dirs=[Path('source')],
            package_omit=['__pycache__', 'RCS'],
        ),
    ),
])
def test_update(left, right, expected):
    left.update(right)
    assert left == expected

@pytest.mark.parametrize('select,ignore,expected', [
    (None, None, set(Check)),
    (None, {Check.W201, Check.W202}, set(Check) - {Check.W201, Check.W202}),
    ({Check.W201, Check.W202}, None, {Check.W201, Check.W202}),
    ({Check.W201, Check.W202}, {Check.W001, Check.W201}, {Check.W202}),
])
def test_get_selected_checks(select, ignore, expected):
    select_copy = select and select.copy()
    cfg = Configuration(select=select, ignore=ignore)
    assert cfg.get_selected_checks() == expected
    assert cfg.select == select_copy

def test_get_package_tree_both_none():
    cfg = Configuration(package_paths=None, src_dirs=None)
    assert cfg.get_package_tree() is None

@pytest.mark.parametrize('package_omit,exclude', [
    (None, TRAVERSAL_EXCLUSIONS),
    ([], []),
    (['__pycache__', 'RCS'], ['__pycache__', 'RCS']),
])
def test_get_package_tree_package_path(mocker, package_omit, exclude):
    path = Path('foobar')
    cfg = Configuration(package_paths=[path], package_omit=package_omit)
    tree = Directory(
        path=None,
        entries={
            "foobar": Directory(
                path="foobar/",
                entries={
                    "__init__.py": File(
                        ('foobar', '__init__.py'),
                        None,
                        None,
                    ),
                    "foo.py": File(
                        ('foobar', 'foo.py'),
                        None,
                        None,
                    ),
                    "bar.py": File(
                        ('foobar', 'bar.py'),
                        None,
                        None,
                    ),
                },
            ),
        },
    )
    fltmock = mocker.patch.object(Directory, 'from_local_tree', return_value=tree)
    assert cfg.get_package_tree() == tree
    fltmock.assert_called_once_with(path, exclude=exclude)

@pytest.mark.parametrize('package_omit,exclude', [
    (None, TRAVERSAL_EXCLUSIONS),
    ([], []),
    (['__pycache__', 'RCS'], ['__pycache__', 'RCS']),
])
def test_get_package_tree_src_dir(mocker, package_omit, exclude):
    path = Path('src')
    cfg = Configuration(src_dirs=[path], package_omit=package_omit)
    tree = Directory(
        path=None,
        entries={
            "foobar": Directory(
                path="foobar/",
                entries={
                    "__init__.py": File(('foobar', '__init__.py'), None, None),
                    "foo.py": File(('foobar', 'foo.py'), None, None),
                    "bar.py": File(('foobar', 'bar.py'), None, None),
                },
            ),
        },
    )
    fltmock = mocker.patch.object(Directory, 'from_local_tree', return_value=tree)
    assert cfg.get_package_tree() == tree
    fltmock.assert_called_once_with(path, exclude=exclude, include_root=False)

def test_get_package_tree_multiple_package_paths(fs):
    fs.create_file('/usr/src/project/foo.py')
    fs.create_file('/usr/src/project/bar/__init__.py')
    fs.create_file('/usr/src/project/bar/quux.py')
    fs.create_file('/usr/src/project/bar/glarch.py')
    fs.cwd = '/usr/src/project'
    cfg = Configuration(package_paths=[Path('foo.py'), Path('bar')])
    assert cfg.get_package_tree() == Directory(
        path=None,
        entries={
            "foo.py": File(('foo.py',), None, None),
            "bar": Directory(
                path='bar/',
                entries={
                    "__init__.py": File(('bar', '__init__.py'), None, None),
                    "quux.py": File(('bar', 'quux.py'), None, None),
                    "glarch.py": File(('bar', 'glarch.py'), None, None),
                },
            ),
        },
    )

def test_get_package_tree_multiple_src_dirs(fs):
    fs.create_file('/usr/src/project/src/foo.py')
    fs.create_file('/usr/src/project/source/bar/__init__.py')
    fs.create_file('/usr/src/project/source/bar/quux.py')
    fs.create_file('/usr/src/project/source/bar/glarch.py')
    fs.cwd = '/usr/src/project'
    cfg = Configuration(src_dirs=[Path('src'), Path('source')])
    assert cfg.get_package_tree() == Directory(
        path=None,
        entries={
            "foo.py": File(('foo.py',), None, None),
            "bar": Directory(
                path='bar/',
                entries={
                    "__init__.py": File(('bar', '__init__.py'), None, None),
                    "quux.py": File(('bar', 'quux.py'), None, None),
                    "glarch.py": File(('bar', 'glarch.py'), None, None),
                },
            ),
        },
    )

def test_get_package_tree_package_path_and_src_dir(fs):
    fs.create_file('/usr/src/project/src/foo.py')
    fs.create_file('/usr/src/project/bar/__init__.py')
    fs.create_file('/usr/src/project/bar/quux.py')
    fs.create_file('/usr/src/project/bar/glarch.py')
    fs.cwd = '/usr/src/project'
    cfg = Configuration(package_paths=[Path('bar')], src_dirs=[Path('src')])
    assert cfg.get_package_tree() == Directory(
        path=None,
        entries={
            "foo.py": File(('foo.py',), None, None),
            "bar": Directory(
                path='bar/',
                entries={
                    "__init__.py": File(('bar', '__init__.py'), None, None),
                    "quux.py": File(('bar', 'quux.py'), None, None),
                    "glarch.py": File(('bar', 'glarch.py'), None, None),
                },
            ),
        },
    )

def test_get_package_tree_package_paths_conflict(fs):
    fs.create_file('/usr/src/project/bar/__init__.py')
    fs.create_file('/usr/src/project/bar/quux.py')
    fs.create_file('/usr/src/project/bar/glarch.py')
    fs.create_file('/usr/src/project/src/bar/gnusto.py')
    fs.cwd = '/usr/src/project'
    cfg = Configuration(package_paths=[Path('bar'), Path('src/bar')])
    with pytest.raises(UserInputError) as excinfo:
        cfg.get_package_tree()
    assert str(excinfo.value) == (
        "`--package src/bar` adds 'bar' to file tree, but it is already"
        " present from prior --package option"
    )

def test_get_package_tree_src_dirs_conflict(fs):
    fs.create_file('/usr/src/project/source/bar/__init__.py')
    fs.create_file('/usr/src/project/source/bar/quux.py')
    fs.create_file('/usr/src/project/source/bar/glarch.py')
    fs.create_file('/usr/src/project/src/bar/gnusto.py')
    fs.cwd = '/usr/src/project'
    cfg = Configuration(src_dirs=[Path('source'), Path('src')])
    with pytest.raises(UserInputError) as excinfo:
        cfg.get_package_tree()
    assert str(excinfo.value) == (
        "`--src-dir src` adds 'bar' to file tree, but it is already present"
        " from prior --package or --src-dir option"
    )

def test_get_package_tree_package_path_src_dir_conflict(fs):
    fs.create_file('/usr/src/project/bar/__init__.py')
    fs.create_file('/usr/src/project/bar/quux.py')
    fs.create_file('/usr/src/project/bar/glarch.py')
    fs.create_file('/usr/src/project/src/bar/gnusto.py')
    fs.cwd = '/usr/src/project'
    cfg = Configuration(package_paths=[Path('bar')], src_dirs=[Path('src')])
    with pytest.raises(UserInputError) as excinfo:
        cfg.get_package_tree()
    assert str(excinfo.value) == (
        "`--src-dir src` adds 'bar' to file tree, but it is already present"
        " from prior --package or --src-dir option"
    )
