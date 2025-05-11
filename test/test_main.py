from __future__ import annotations
import json
from operator import attrgetter
from pathlib import Path
from traceback import format_exception
from typing import Any
from click.testing import CliRunner, Result
import pytest
from pytest_mock import MockerFixture
from check_wheel_contents.__main__ import main
from check_wheel_contents.checker import NO_CONFIG
from check_wheel_contents.checks import Check

WHEEL_DIR = Path(__file__).with_name("data") / "wheels"


def show_result(r: Result) -> str:
    if r.exception is not None:
        assert isinstance(r.exc_info, tuple)
        return "".join(format_exception(*r.exc_info))
    else:
        return r.output


@pytest.mark.parametrize(
    "options,configargs",
    [
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
            ["--no-config"],
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
            ["--config", "foo.cfg"],
            {
                "configpath": "foo.cfg",
                "select": None,
                "ignore": None,
                "toplevel": None,
                "package": (),
                "src_dir": (),
                "package_omit": None,
            },
        ),
        (
            ["--config", "foo.cfg", "--no-config"],
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
            ["--no-config", "--config", "foo.cfg"],
            {
                "configpath": "foo.cfg",
                "select": None,
                "ignore": None,
                "toplevel": None,
                "package": (),
                "src_dir": (),
                "package_omit": None,
            },
        ),
        (
            ["--select", "W001,W2", "--ignore=W201"],
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
            ["--toplevel", "foo,bar/"],
            {
                "configpath": None,
                "select": None,
                "ignore": None,
                "toplevel": ["foo", "bar/"],
                "package": (),
                "src_dir": (),
                "package_omit": None,
            },
        ),
        (
            ["--package=foo", "--src-dir", "src"],
            {
                "configpath": None,
                "select": None,
                "ignore": None,
                "toplevel": None,
                "package": ("foo",),
                "src_dir": ("src",),
                "package_omit": None,
            },
        ),
        (
            ["--package-omit", "__*__, test/data"],
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
            ["--package-omit", ""],
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
    ],
)
def test_options2configargs(
    mocker: MockerFixture,
    monkeypatch: pytest.MonkeyPatch,
    options: list[str],
    configargs: dict[str, Any],
    tmp_path: Path,
) -> None:
    (tmp_path / "foo").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "foo.cfg").touch()
    monkeypatch.chdir(tmp_path)
    mock_checker = mocker.patch(
        "check_wheel_contents.__main__.WheelChecker",
        autospec=True,
    )
    r = CliRunner().invoke(main, options)
    assert r.exit_code == 0, show_result(r)
    assert mock_checker.method_calls == [mocker.call().configure_options(**configargs)]


@pytest.mark.parametrize(
    "options",
    [
        ["--select=W9999"],
        ["--ignore", "W9999"],
    ],
)
def test_bad_checks_option_error(mocker: MockerFixture, options: list[str]) -> None:
    mock_checker = mocker.patch(
        "check_wheel_contents.__main__.WheelChecker",
        autospec=True,
    )
    r = CliRunner().invoke(main, options)
    assert r.exit_code != 0, show_result(r)
    assert "Unknown/invalid check prefix: 'W9999'" in r.output
    mock_checker.assert_not_called()


@pytest.mark.parametrize(
    "whlfile",
    WHEEL_DIR.glob("*.whl"),
    ids=attrgetter("name"),
)
def test_main(monkeypatch: pytest.MonkeyPatch, whlfile: Path) -> None:
    with whlfile.with_suffix(".json").open() as fp:
        expected = json.load(fp)
    monkeypatch.chdir(str(WHEEL_DIR))
    r = CliRunner().invoke(main, ["--no-config", whlfile.name])
    assert r.exit_code == expected["rc"], show_result(r)
    assert r.stdout.rstrip() == expected["stdout"]
    assert r.stderr.rstrip() == expected["stderr"]


@pytest.mark.parametrize(
    "cfgname,cfgsrc,errmsg",
    [
        (
            "foo.ini",
            "[check-wheel-contents]\nselect = W9\n",
            "Unknown/invalid check prefix: 'W9'",
        ),
        (
            "foo.toml",
            '[tool.check-wheel-contents]\nignore = [""]\n',
            "Unknown/invalid check prefix: ''",
        ),
        (
            "foo.cfg",
            "[check-wheel-contents]\npackage = missing\n",
            "package: no such file or directory: {missing_path!r}",
        ),
        (
            "foo.cfg",
            "[check-wheel-contents]\nsrc_dir = missing\n",
            "src_dir: not a directory: {missing_path!r}",
        ),
    ],
)
def test_bad_config_error(
    cfgname: str,
    cfgsrc: str,
    errmsg: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    Path(cfgname).write_text(cfgsrc)
    r = CliRunner().invoke(main, ["--config", cfgname])
    assert r.exit_code != 0, show_result(r)
    assert f"Error: {cfgname}: " in r.output
    assert errmsg.format(missing_path=str(tmp_path / "missing")) in r.output
