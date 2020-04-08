import json
from   operator                      import attrgetter
from   pathlib                       import Path
from   traceback                     import format_exception
from   click.testing                 import CliRunner
import pytest
from   check_wheel_contents.__main__ import main
from   check_wheel_contents.checker  import NO_CONFIG
from   check_wheel_contents.checks   import Check

WHEEL_DIR = Path(__file__).with_name('data') / 'wheels'

def show_result(r):
    if r.exception is not None:
        return ''.join(format_exception(*r.exc_info))
    else:
        return r.output

@pytest.mark.parametrize('options,configargs', [
    (
        [],
        {
            "configpath": None,
            "select": None,
            "ignore": None,
            "toplevel": None,
            "package": (),
            "src_dir": (),
            "package_omit": None,
        },
    ),

    (
        ['--no-config'],
        {
            "configpath": NO_CONFIG,
            "select": None,
            "ignore": None,
            "toplevel": None,
            "package": (),
            "src_dir": (),
            "package_omit": None,
        },
    ),

    (
        ['--config', 'foo.cfg'],
        {
            "configpath": 'foo.cfg',
            "select": None,
            "ignore": None,
            "toplevel": None,
            "package": (),
            "src_dir": (),
            "package_omit": None,
        },
    ),

    (
        ['--config', 'foo.cfg', '--no-config'],
        {
            "configpath": NO_CONFIG,
            "select": None,
            "ignore": None,
            "toplevel": None,
            "package": (),
            "src_dir": (),
            "package_omit": None,
        },
    ),

    (
        ['--no-config', '--config', 'foo.cfg'],
        {
            "configpath": 'foo.cfg',
            "select": None,
            "ignore": None,
            "toplevel": None,
            "package": (),
            "src_dir": (),
            "package_omit": None,
        },
    ),

    (
        ['--select', 'W001,W2', '--ignore=W201'],
        {
            "configpath": None,
            "select": {Check.W001, Check.W201, Check.W202},
            "ignore": {Check.W201},
            "toplevel": None,
            "package": (),
            "src_dir": (),
            "package_omit": None,
        },
    ),

    (
        ['--toplevel', 'foo,bar/'],
        {
            "configpath": None,
            "select": None,
            "ignore": None,
            "toplevel": ['foo', 'bar/'],
            "package": (),
            "src_dir": (),
            "package_omit": None,
        },
    ),

    (
        ['--package=foo', '--src-dir', 'src'],
        {
            "configpath": None,
            "select": None,
            "ignore": None,
            "toplevel": None,
            "package": ('foo',),
            "src_dir": ('src',),
            "package_omit": None,
        },
    ),

    (
        ['--package-omit', '__*__, test/data'],
        {
            "configpath": None,
            "select": None,
            "ignore": None,
            "toplevel": None,
            "package": (),
            "src_dir": (),
            "package_omit": ["__*__", "test/data"],
        },
    ),

    (
        ['--package-omit', ''],
        {
            "configpath": None,
            "select": None,
            "ignore": None,
            "toplevel": None,
            "package": (),
            "src_dir": (),
            "package_omit": [],
        },
    ),
])
def test_options2configargs(fs, mocker, options, configargs):
    fs.create_dir('/usr/src/project/foo')
    fs.create_dir('/usr/src/project/src')
    fs.create_file('/usr/src/project/foo.cfg')
    fs.cwd = '/usr/src/project'
    mock_checker = mocker.patch(
        'check_wheel_contents.__main__.WheelChecker',
        autospec=True,
    )
    r = CliRunner().invoke(main, options)
    assert r.exit_code == 0, show_result(r)
    assert mock_checker.method_calls \
        == [mocker.call().configure_options(**configargs)]

@pytest.mark.parametrize('options', [
    ['--select=W9999'],
    ['--ignore', 'W9999'],
])
def test_bad_checks_option_error(mocker, options):
    mock_checker = mocker.patch(
        'check_wheel_contents.__main__.WheelChecker',
        autospec=True,
    )
    r = CliRunner().invoke(main, options)
    assert r.exit_code != 0, show_result(r)
    assert "Unknown/invalid check prefix: 'W9999'" in r.output
    mock_checker.assert_not_called()

@pytest.mark.parametrize('whlfile', [
    p for p in WHEEL_DIR.iterdir() if p.suffix == '.whl'
], ids=attrgetter("name"))
def test_main(monkeypatch, whlfile):
    with open(str(whlfile.with_suffix('.json'))) as fp:
        expected = json.load(fp)
    monkeypatch.chdir(str(WHEEL_DIR))
    r = CliRunner(mix_stderr=False).invoke(main, ['--no-config', whlfile.name])
    assert r.exit_code == expected["rc"], show_result(r)
    assert r.stdout.rstrip() == expected["stdout"]
    assert r.stderr.rstrip() == expected["stderr"]
