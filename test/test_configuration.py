from   pathlib                     import Path
from   unittest.mock               import sentinel
import attr
import pytest
from   check_wheel_contents.checks import Check
from   check_wheel_contents.config import ConfigDict, Configuration

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
def test_from_command_options(toplevel_in, toplevel_out, package_in,
                              package_out, src_dir_in, src_dir_out):
    cfg = Configuration.from_command_options(
        select = sentinel.SELECT,
        ignore = sentinel.IGNORE,
        toplevel = toplevel_in,
        package = package_in,
        src_dir = src_dir_in,
    )
    assert attr.asdict(cfg, retain_collection_types=True) == {
        "select": sentinel.SELECT,
        "ignore": sentinel.IGNORE,
        "toplevel": toplevel_out,
        "package_paths": package_out,
        "src_dirs": src_dir_out,
    }

def test_from_command_options_default():
    cfg = Configuration.from_command_options()
    assert attr.asdict(cfg, retain_collection_types=True) == {
        "select": None,
        "ignore": None,
        "toplevel": None,
        "package_paths": None,
        "src_dirs": None,
    }

def test_from_config_dict_calls(mocker):
    cd = mocker.Mock(
        ConfigDict,
        **{
            "get_comma_list.return_value": ["foo.py", "bar/"],
            "get_check_set.return_value": sentinel.CHECK_SET,
            "get_path_list.return_value": sentinel.PATH_LIST,
        },
    )
    cfg = Configuration.from_config_dict(cd)
    assert attr.asdict(cfg, retain_collection_types=True) == {
        "select": sentinel.CHECK_SET,
        "ignore": sentinel.CHECK_SET,
        "toplevel": ["foo.py", "bar"],
        "package_paths": sentinel.PATH_LIST,
        "src_dirs": sentinel.PATH_LIST,
    }
    assert cd.get_check_set.call_count == 2
    cd.get_check_set.assert_any_call("select")
    cd.get_check_set.assert_any_call("ignore")
    cd.get_comma_list.assert_called_once_with("toplevel")
    assert cd.get_path_list.call_count == 2
    cd.get_path_list.assert_any_call("package")
    cd.get_path_list.assert_any_call("src_dir")

@pytest.mark.parametrize('cfgdict,expected', [
    (
        ConfigDict(configpath=Path('foo.cfg'), data={}),
        Configuration(
            select = None,
            ignore = None,
            toplevel = None,
            package_paths = None,
            src_dirs = None,
        ),
    ),
    (
        ConfigDict(
            configpath=Path('/usr/src/project/cfg.ini'),
            data={
                "select": "W001,W002",
                "ignore": "W003,W004",
                "toplevel": "foo.py,bar/",
                "package": "foobar",
                "src_dir": "src",
            },
        ),
        Configuration(
            select = {Check.W001, Check.W002},
            ignore = {Check.W003, Check.W004},
            toplevel = ["foo.py", "bar"],
            package_paths = [Path('/usr/src/project/foobar')],
            src_dirs = [Path('/usr/src/project/src')],
        ),
    ),
    (
        ConfigDict(
            configpath=Path('/usr/src/project/cfg.ini'),
            data={
                "select": ["W001", "W002"],
                "ignore": ["W003", "W004"],
                "toplevel": ["foo.py", "bar/"],
                "package": ["foobar"],
                "src_dir": ["src"],
            },
        ),
        Configuration(
            select = {Check.W001, Check.W002},
            ignore = {Check.W003, Check.W004},
            toplevel = ["foo.py", "bar"],
            package_paths = [Path('/usr/src/project/foobar')],
            src_dirs = [Path('/usr/src/project/src')],
        ),
    ),
    (
        ConfigDict(
            configpath=Path('/usr/src/project/cfg.ini'),
            data={
                "toplevel": "",
                "package": "",
                "src_dir": "",
            },
        ),
        Configuration(
            select = None,
            ignore = None,
            toplevel = [],
            package_paths = [],
            src_dirs = [],
        ),
    ),
    (
        ConfigDict(
            configpath=Path('/usr/src/project/cfg.ini'),
            data={
                "toplevel": [],
                "package": [],
                "src_dir": [],
            },
        ),
        Configuration(
            select = None,
            ignore = None,
            toplevel = [],
            package_paths = [],
            src_dirs = [],
        ),
    ),
])
def test_from_config_dict(cfgdict, expected):
    assert Configuration.from_config_dict(cfgdict) == expected

@pytest.mark.parametrize('cfgdict', [
    None,
    ConfigDict(
        configpath=Path('/usr/src/project/cfg.ini'),
        data={
            "select": "W001,W002",
            "ignore": "W003,W004",
            "toplevel": "foo.py,bar/",
            "package": "foobar",
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
        configpath=Path('/usr/src/project/cfg.ini'),
        data={
            "select": "W001,W002",
            "ignore": "W003,W004",
            "toplevel": "foo.py,bar/",
            "package": "foobar",
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
        configpath=Path('/usr/src/project/cfg.ini'),
        data={
            "select": "W001,W002",
            "ignore": "W003,W004",
            "toplevel": "foo.py,bar/",
            "package": "foobar",
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
