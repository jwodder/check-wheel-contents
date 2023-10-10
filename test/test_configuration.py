from __future__ import annotations
import json
from operator import attrgetter
import os
from pathlib import Path
from shutil import copytree
from typing import Any
from pydantic import ValidationError
import pytest
from pytest_mock import MockerFixture
from check_wheel_contents.checks import Check
from check_wheel_contents.config import TRAVERSAL_EXCLUSIONS, Configuration
from check_wheel_contents.errors import UserInputError
from check_wheel_contents.filetree import Directory, File

DATA_DIR = Path(__file__).with_name("data")
PROJECT_TREE = DATA_DIR / "project-tree"


def create_file(p: Path, contents: str | None = None) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    if contents is not None:
        p.write_text(contents, encoding="UTF-8")
    else:
        p.touch()


@pytest.mark.parametrize(
    "files,cfg",
    [
        (
            {
                "usr/src/project/pyproject.toml": (
                    '[tool.check-wheel-contents]\nselect = "W001"\n'
                ),
                "usr/src/project/tox.ini": "[check-wheel-contents]\nselect = W002\n",
                "usr/src/project/setup.cfg": (
                    "[tool:check-wheel-contents]\nselect = W003\n"
                ),
                "usr/src/project/check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W004\n"
                ),
                "usr/src/project/.check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W005\n"
                ),
            },
            Configuration(select={Check.W001}),
        ),
        (
            {
                "usr/src/project/pyproject.toml": "",
                "usr/src/project/tox.ini": "[check-wheel-contents]\nselect = W002\n",
                "usr/src/project/setup.cfg": (
                    "[tool:check-wheel-contents]\nselect = W003\n"
                ),
                "usr/src/project/check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W004\n"
                ),
                "usr/src/project/.check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W005\n"
                ),
            },
            Configuration(select={Check.W002}),
        ),
        (
            {
                "usr/src/project/tox.ini": "[check-wheel-contents]\nselect = W002\n",
                "usr/src/project/setup.cfg": (
                    "[tool:check-wheel-contents]\nselect = W003\n"
                ),
                "usr/src/project/check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W004\n"
                ),
                "usr/src/project/.check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W005\n"
                ),
            },
            Configuration(select={Check.W002}),
        ),
        (
            {
                "usr/src/project/tox.ini": "",
                "usr/src/project/setup.cfg": (
                    "[tool:check-wheel-contents]\nselect = W003\n"
                ),
                "usr/src/project/check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W004\n"
                ),
                "usr/src/project/.check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W005\n"
                ),
            },
            Configuration(select={Check.W003}),
        ),
        (
            {
                "usr/src/project/setup.cfg": (
                    "[tool:check-wheel-contents]\nselect = W003\n"
                ),
                "usr/src/project/check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W004\n"
                ),
                "usr/src/project/.check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W005\n"
                ),
            },
            Configuration(select={Check.W003}),
        ),
        (
            {
                "usr/src/project/setup.cfg": "",
                "usr/src/project/check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W004\n"
                ),
                "usr/src/project/.check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W005\n"
                ),
            },
            Configuration(select={Check.W004}),
        ),
        (
            {
                "usr/src/project/check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W004\n"
                ),
                "usr/src/project/.check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W005\n"
                ),
            },
            Configuration(select={Check.W004}),
        ),
        (
            {
                "usr/src/project/check-wheel-contents.cfg": "",
                "usr/src/project/.check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W005\n"
                ),
            },
            Configuration(select={Check.W005}),
        ),
        (
            {
                "usr/src/project/.check-wheel-contents.cfg": (
                    "[check-wheel-contents]\nselect = W005\n"
                ),
            },
            Configuration(select={Check.W005}),
        ),
        (
            {"usr/src/project/.check-wheel-contents.cfg": ""},
            None,
        ),
        ({}, None),
        (
            {
                "usr/src/tox.ini": "[check-wheel-contents]\nselect = W002\n",
                "usr/src/project/setup.cfg": (
                    "[tool:check-wheel-contents]\nselect = W003\n"
                ),
            },
            Configuration(select={Check.W003}),
        ),
        (
            {
                "usr/src/tox.ini": "[check-wheel-contents]\nselect = W002\n",
                "usr/src/project/setup.cfg": "",
            },
            None,
        ),
        (
            {
                "usr/src/tox.ini": "[check-wheel-contents]\nselect = W002\n",
            },
            Configuration(select={Check.W002}),
        ),
        (
            {
                "usr/src/tox.ini": "[check-wheel-contents]\nselect = W002\n",
                "usr/pyproject.toml": (
                    '[tool.check-wheel-contents]\nselect = "W001"\n'
                ),
            },
            Configuration(select={Check.W002}),
        ),
        (
            {
                "usr/src/tox.ini": "",
                "usr/pyproject.toml": (
                    '[tool.check-wheel-contents]\nselect = "W001"\n'
                ),
            },
            None,
        ),
        (
            {
                "usr/pyproject.toml": (
                    '[tool.check-wheel-contents]\nselect = "W001"\n'
                ),
            },
            Configuration(select={Check.W001}),
        ),
        (
            {
                "usr/src/setup.cfg": "[tool:check-wheel-contents]\nselect = W003\n",
            },
            Configuration(select={Check.W003}),
        ),
    ],
)
def test_find_default(
    files: dict[str, str],
    cfg: Configuration,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    for path, text in files.items():
        create_file(tmp_path / path, text)
    pwd = tmp_path / "usr" / "src" / "project"
    pwd.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(pwd)
    assert Configuration.find_default() == cfg


@pytest.mark.parametrize(
    "path",
    [p for p in (DATA_DIR / "configfiles").iterdir() if p.suffix != ".json"],
    ids=attrgetter("name"),
)
def test_from_file(path: Path) -> None:
    datafile = path.with_suffix(".json")
    try:
        data = json.loads(datafile.read_text())
    except FileNotFoundError:
        cfg = None
    else:
        cfg = Configuration.model_validate(data)
    assert Configuration.from_file(path) == cfg


@pytest.mark.parametrize(
    "cfgname,cfgsrc",
    [
        (
            "cfg.ini",
            "[check-wheel-contents]\n"
            "select = W001,W002\n"
            "ignore = W003,W004\n"
            "toplevel = foo.py,quux/\n"
            "package = bar\n"
            "src_dir = src\n"
            "package_omit = __pycache__,test/data\n",
        ),
        (
            "cfg.toml",
            "[tool.check-wheel-contents]\n"
            'select = ["W001", "W002"]\n'
            'ignore = ["W003", "W004"]\n'
            'toplevel = ["foo.py", "quux/"]\n'
            'package = ["bar"]\n'
            'src_dir = ["src"]\n'
            'package_omit = ["__pycache__", "test/data"]\n',
        ),
    ],
)
def test_from_file_in_project(cfgname: str, cfgsrc: str, tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    copytree(PROJECT_TREE, project_dir)
    cfgpath = project_dir / cfgname
    cfgpath.write_text(cfgsrc)
    assert Configuration.from_file(cfgpath) == Configuration(
        select={Check.W001, Check.W002},
        ignore={Check.W003, Check.W004},
        toplevel=["foo.py", "quux"],
        package_paths=[project_dir / "bar"],
        src_dirs=[project_dir / "src"],
        package_omit=["__pycache__", "test/data"],
    )


def test_from_file_bad_tool_section() -> None:
    path = DATA_DIR / "bad-tool-sect.toml"
    with pytest.raises(UserInputError) as excinfo:
        Configuration.from_file(path)
    assert str(excinfo.value).startswith(f"{path}: ")


@pytest.mark.parametrize(
    "data,expected",
    [
        ({}, None),
        ({"package_omit": ""}, []),
        ({"package_omit": "foo"}, ["foo"]),
        ({"package_omit": "foo, bar,"}, ["foo", "bar"]),
        ({"package_omit": ["foo", "bar"]}, ["foo", "bar"]),
        ({"package_omit": ["foo, bar,"]}, ["foo, bar,"]),
    ],
)
def test_convert_comma_list(data: dict[str, Any], expected: list[str] | None) -> None:
    cfg = Configuration.model_validate(data)
    assert cfg.package_omit == expected


@pytest.mark.parametrize(
    "field",
    [
        "select",
        "ignore",
        "toplevel",
        "package",
        "src_dir",
        "package_omit",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        42,
        True,
        [42],
        ["foo", 42],
        ["foo", None],
    ],
)
def test_convert_comma_list_error(field: str, value: Any) -> None:
    with pytest.raises(ValidationError):
        Configuration.model_validate({field: value})


@pytest.mark.parametrize(
    "data,expected",
    [
        ({}, None),
        ({"select": ""}, set()),
        ({"select": "W001"}, {Check.W001}),
        ({"select": "W001, W002,"}, {Check.W001, Check.W002}),
        ({"select": ["W001", "W002"]}, {Check.W001, Check.W002}),
    ],
)
def test_convert_check_set(data: dict[str, Any], expected: set[Check] | None) -> None:
    cfg = Configuration.model_validate(data)
    assert cfg.select == expected


@pytest.mark.parametrize("field", ["select", "ignore"])
@pytest.mark.parametrize(
    "value,badbit",
    [
        (["W001, W002,"], "W001, W002,"),
        (["W", ""], ""),
        (["W9", ""], "W9"),
    ],
)
def test_convert_check_set_error(field: str, value: list[str], badbit: str) -> None:
    with pytest.raises(ValidationError) as excinfo:
        Configuration.model_validate({field: value})
    assert f"Unknown/invalid check prefix: {badbit!r}" in str(excinfo.value)


BASE = Path("usr/src/project/path")


@pytest.mark.parametrize(
    "data,expected",
    [
        ({}, None),
        ({"package": ""}, []),
        ({"package": "foo"}, [BASE / "foo"]),
        (
            {"package": "foo, bar/, test/data, {tmp_path}/usr/src"},
            [BASE / "foo", BASE / "bar", BASE / "test" / "data", Path("usr/src")],
        ),
        (
            {"package": ["foo", "bar,baz", "test/data", "{tmp_path}/usr/src"]},
            [BASE / "foo", BASE / "bar,baz", BASE / "test" / "data", Path("usr/src")],
        ),
    ],
)
def test_resolve_paths(
    data: dict[str, str | list[str]],
    expected: list[Path] | None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    for path in [
        "usr/src/project/path/foo",
        "usr/src/project/path/bar",
        "usr/src/project/path/bar,baz",
        "usr/src/project/path/test/data",
    ]:
        create_file(tmp_path / path)
    monkeypatch.chdir(tmp_path / "usr" / "src" / "project")
    if "package" in data:
        if isinstance(data["package"], str):
            data["package"] = data["package"].format(tmp_path=tmp_path)
        elif isinstance(data["package"], list):
            data["package"] = [p.format(tmp_path=tmp_path) for p in data["package"]]
    cfg = Configuration.model_validate(data)
    cfg.resolve_paths(Path("path/foo.cfg"))
    if expected is not None:
        expected = [tmp_path / p for p in expected]
    assert cfg.package_paths == expected


def test_resolve_paths_nonexistent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    create_file(tmp_path / "path/foo")
    create_file(tmp_path / "path/bar")
    monkeypatch.chdir(tmp_path)
    cfg = Configuration(package_paths="foo,bar,quux")
    with pytest.raises(UserInputError) as excinfo:
        cfg.resolve_paths(Path("path/foo.cfg"))
    assert str(excinfo.value) == (
        "package: no such file or directory: {!r}".format(
            str(tmp_path / "path" / "quux")
        )
    )


def test_resolve_paths_require_dir_not_a_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    create_file(tmp_path / "path/foo")
    create_file(tmp_path / "path/bar")
    monkeypatch.chdir(tmp_path)
    cfg = Configuration(src_dirs="foo,bar,quux")
    with pytest.raises(UserInputError) as excinfo:
        cfg.resolve_paths(Path("path/foo.cfg"))
    assert str(excinfo.value) == "src_dir: not a directory: {!r}".format(
        str(tmp_path / "path" / "foo")
    )


@pytest.mark.parametrize(
    "toplevel_in,toplevel_out",
    [
        (None, None),
        (["foo.py", "bar"], ["foo.py", "bar"]),
        (["foo.py", "bar/"], ["foo.py", "bar"]),
    ],
)
@pytest.mark.parametrize(
    "package_in,package_out",
    [
        ((), None),
        (("foo.py", "bar"), [Path("foo.py"), Path("bar")]),
    ],
)
@pytest.mark.parametrize(
    "src_dir_in,src_dir_out",
    [
        ((), None),
        (("quux",), [Path("quux")]),
    ],
)
@pytest.mark.parametrize(
    "package_omit_in,package_omit_out",
    [
        (None, None),
        ([], []),
        (["RCS", "*.pyc"], ["RCS", "*.pyc"]),
    ],
)
def test_from_command_options(
    toplevel_in: list[str] | None,
    toplevel_out: list[str] | None,
    package_in: tuple[str, ...],
    package_out: list[Path] | None,
    src_dir_in: tuple[str, ...],
    src_dir_out: list[Path] | None,
    package_omit_in: list[str] | None,
    package_omit_out: list[str] | None,
) -> None:
    cfg = Configuration.from_command_options(
        select={Check.W001, Check.W002},
        ignore={Check.W003, Check.W004},
        toplevel=toplevel_in,
        package=package_in,
        src_dir=src_dir_in,
        package_omit=package_omit_in,
    )
    assert cfg.model_dump() == {
        "select": {Check.W001, Check.W002},
        "ignore": {Check.W003, Check.W004},
        "toplevel": toplevel_out,
        "package_paths": package_out,
        "src_dirs": src_dir_out,
        "package_omit": package_omit_out,
    }


def test_from_command_options_default() -> None:
    cfg = Configuration.from_command_options()
    assert cfg.model_dump() == {
        "select": None,
        "ignore": None,
        "toplevel": None,
        "package_paths": None,
        "src_dirs": None,
        "package_omit": None,
    }


@pytest.mark.parametrize(
    "cfg",
    [
        None,
        Configuration(
            select={Check.W001, Check.W002},
            ignore={Check.W003, Check.W004},
            toplevel=["foo.py", "quux"],
            package_paths=[PROJECT_TREE / "bar"],
            src_dirs=[PROJECT_TREE / "src"],
            package_omit=["__pycache__", "test/data"],
        ),
    ],
)
def test_from_config_file(mocker: MockerFixture, cfg: Configuration | None) -> None:
    """
    Test that calling ``Configuration.from_config_file(path)`` delegates to
    ``Configuration.from_file()`` and that `None` return values are converted
    to a default-valued `Configuration`
    """
    mock = mocker.patch.object(Configuration, "from_file", return_value=cfg)
    if cfg is None:
        expected = Configuration()
    else:
        expected = cfg
    path = "/foo/bar/quux"
    assert Configuration.from_config_file(path) == expected
    mock.assert_called_once_with(Path(path))


@pytest.mark.parametrize(
    "cfg",
    [
        None,
        Configuration(
            select={Check.W001, Check.W002},
            ignore={Check.W003, Check.W004},
            toplevel=["foo.py", "quux"],
            package_paths=[PROJECT_TREE / "bar"],
            src_dirs=[PROJECT_TREE / "src"],
            package_omit=["__pycache__", "test/data"],
        ),
    ],
)
def test_from_config_file_none_path(
    mocker: MockerFixture, cfg: Configuration | None
) -> None:
    """
    Test that calling ``Configuration.from_config_file(None)`` delegates to
    ``Configuration.find_default()`` and that `None` return values are
    converted to a default-valued `Configuration`
    """
    mock = mocker.patch.object(Configuration, "find_default", return_value=cfg)
    if cfg is None:
        expected = Configuration()
    else:
        expected = cfg
    assert Configuration.from_config_file(None) == expected
    mock.assert_called_once_with()


@pytest.mark.parametrize(
    "cfg",
    [
        None,
        Configuration(
            select={Check.W001, Check.W002},
            ignore={Check.W003, Check.W004},
            toplevel=["foo.py", "quux"],
            package_paths=[PROJECT_TREE / "bar"],
            src_dirs=[PROJECT_TREE / "src"],
            package_omit=["__pycache__", "test/data"],
        ),
    ],
)
def test_from_config_file_no_arg(
    mocker: MockerFixture, cfg: Configuration | None
) -> None:
    """
    Test that calling ``Configuration.from_config_file()`` with no arguments
    delegates to ``Configuration.find_default()`` and that `None` return values
    are converted to a default-valued `Configuration`
    """
    mock = mocker.patch.object(Configuration, "find_default", return_value=cfg)
    if cfg is None:
        expected = Configuration()
    else:
        expected = cfg
    assert Configuration.from_config_file() == expected
    mock.assert_called_once_with()


@pytest.mark.parametrize(
    "left,right,expected",
    [
        (Configuration(), Configuration(), Configuration()),
        (
            Configuration(
                select={Check.W001, Check.W002},
                ignore={Check.W003, Check.W004},
                toplevel=["foo.py", "bar"],
                package_paths=[Path("foobar")],
                src_dirs=[Path("src")],
                package_omit=["__pycache__", "RCS"],
            ),
            Configuration(
                select={Check.W005, Check.W006},
                ignore={Check.W007, Check.W008},
                toplevel=["quux", "glarch.py"],
                package_paths=[Path("baz.py")],
                src_dirs=[Path("source")],
                package_omit=["*.pyc", "CVS"],
            ),
            Configuration(
                select={Check.W005, Check.W006},
                ignore={Check.W007, Check.W008},
                toplevel=["quux", "glarch.py"],
                package_paths=[Path("baz.py")],
                src_dirs=[Path("source")],
                package_omit=["*.pyc", "CVS"],
            ),
        ),
        (
            Configuration(
                select={Check.W001, Check.W002},
                ignore={Check.W003, Check.W004},
                toplevel=["foo.py", "bar"],
                package_paths=[Path("foobar")],
                src_dirs=[Path("src")],
                package_omit=["__pycache__", "RCS"],
            ),
            Configuration(
                select=set(),
                ignore=set(),
                toplevel=[],
                package_paths=[],
                src_dirs=[],
                package_omit=[],
            ),
            Configuration(
                select=set(),
                ignore=set(),
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
                toplevel=["foo.py", "bar"],
                package_paths=[Path("foobar")],
                src_dirs=[Path("src")],
                package_omit=["__pycache__", "RCS"],
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
                toplevel=["foo.py", "bar"],
                package_paths=[Path("foobar")],
                src_dirs=[Path("src")],
                package_omit=["__pycache__", "RCS"],
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
                package_paths=[Path("baz.py")],
                src_dirs=[Path("source")],
                package_omit=["__pycache__", "RCS"],
            ),
            Configuration(
                select={Check.W005, Check.W006},
                ignore={Check.W007, Check.W008},
                toplevel=["quux", "glarch.py"],
                package_paths=[Path("baz.py")],
                src_dirs=[Path("source")],
                package_omit=["__pycache__", "RCS"],
            ),
        ),
    ],
)
def test_update(
    left: Configuration, right: Configuration, expected: Configuration
) -> None:
    left.update(right)
    assert left == expected


@pytest.mark.parametrize(
    "select,ignore,expected",
    [
        (None, None, set(Check)),
        (None, {Check.W201, Check.W202}, set(Check) - {Check.W201, Check.W202}),
        ({Check.W201, Check.W202}, None, {Check.W201, Check.W202}),
        ({Check.W201, Check.W202}, {Check.W001, Check.W201}, {Check.W202}),
    ],
)
def test_get_selected_checks(
    select: set[Check] | None, ignore: set[Check] | None, expected: set[Check]
) -> None:
    select_copy = select and select.copy()
    cfg = Configuration(select=select, ignore=ignore)
    assert cfg.get_selected_checks() == expected
    assert cfg.select == select_copy


def test_get_package_tree_both_none() -> None:
    cfg = Configuration(package_paths=None, src_dirs=None)
    assert cfg.get_package_tree() is None


@pytest.mark.parametrize(
    "package_omit,exclude",
    [
        (None, TRAVERSAL_EXCLUSIONS),
        ([], []),
        (["__pycache__", "RCS"], ["__pycache__", "RCS"]),
    ],
)
def test_get_package_tree_package_path(
    mocker: MockerFixture, package_omit: list[str] | None, exclude: list[str]
) -> None:
    path = Path("foobar")
    cfg = Configuration(package_paths=[path], package_omit=package_omit)
    tree = Directory(
        path=None,
        entries={
            "foobar": Directory(
                path="foobar/",
                entries={
                    "__init__.py": File(
                        ("foobar", "__init__.py"),
                        None,
                        None,
                    ),
                    "foo.py": File(
                        ("foobar", "foo.py"),
                        None,
                        None,
                    ),
                    "bar.py": File(
                        ("foobar", "bar.py"),
                        None,
                        None,
                    ),
                },
            ),
        },
    )
    fltmock = mocker.patch.object(Directory, "from_local_tree", return_value=tree)
    assert cfg.get_package_tree() == tree
    fltmock.assert_called_once_with(path, exclude=exclude)


@pytest.mark.parametrize(
    "package_omit,exclude",
    [
        (None, TRAVERSAL_EXCLUSIONS),
        ([], []),
        (["__pycache__", "RCS"], ["__pycache__", "RCS"]),
    ],
)
def test_get_package_tree_src_dir(
    mocker: MockerFixture, package_omit: list[str] | None, exclude: list[str]
) -> None:
    path = Path("src")
    cfg = Configuration(src_dirs=[path], package_omit=package_omit)
    tree = Directory(
        path=None,
        entries={
            "foobar": Directory(
                path="foobar/",
                entries={
                    "__init__.py": File(("foobar", "__init__.py"), None, None),
                    "foo.py": File(("foobar", "foo.py"), None, None),
                    "bar.py": File(("foobar", "bar.py"), None, None),
                },
            ),
        },
    )
    fltmock = mocker.patch.object(Directory, "from_local_tree", return_value=tree)
    assert cfg.get_package_tree() == tree
    fltmock.assert_called_once_with(path, exclude=exclude, include_root=False)


def test_get_package_tree_multiple_package_paths(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    create_file(tmp_path / "foo.py")
    create_file(tmp_path / "bar/__init__.py")
    create_file(tmp_path / "bar/quux.py")
    create_file(tmp_path / "bar/glarch.py")
    monkeypatch.chdir(tmp_path)
    cfg = Configuration(package_paths=[Path("foo.py"), Path("bar")])
    assert cfg.get_package_tree() == Directory(
        path=None,
        entries={
            "foo.py": File(("foo.py",), None, None),
            "bar": Directory(
                path="bar/",
                entries={
                    "__init__.py": File(("bar", "__init__.py"), None, None),
                    "quux.py": File(("bar", "quux.py"), None, None),
                    "glarch.py": File(("bar", "glarch.py"), None, None),
                },
            ),
        },
    )


def test_get_package_tree_multiple_src_dirs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    create_file(tmp_path / "src/foo.py")
    create_file(tmp_path / "source/bar/__init__.py")
    create_file(tmp_path / "source/bar/quux.py")
    create_file(tmp_path / "source/bar/glarch.py")
    monkeypatch.chdir(tmp_path)
    cfg = Configuration(src_dirs=[Path("src"), Path("source")])
    assert cfg.get_package_tree() == Directory(
        path=None,
        entries={
            "foo.py": File(("foo.py",), None, None),
            "bar": Directory(
                path="bar/",
                entries={
                    "__init__.py": File(("bar", "__init__.py"), None, None),
                    "quux.py": File(("bar", "quux.py"), None, None),
                    "glarch.py": File(("bar", "glarch.py"), None, None),
                },
            ),
        },
    )


def test_get_package_tree_package_path_and_src_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    create_file(tmp_path / "src/foo.py")
    create_file(tmp_path / "bar/__init__.py")
    create_file(tmp_path / "bar/quux.py")
    create_file(tmp_path / "bar/glarch.py")
    monkeypatch.chdir(tmp_path)
    cfg = Configuration(package_paths=[Path("bar")], src_dirs=[Path("src")])
    assert cfg.get_package_tree() == Directory(
        path=None,
        entries={
            "foo.py": File(("foo.py",), None, None),
            "bar": Directory(
                path="bar/",
                entries={
                    "__init__.py": File(("bar", "__init__.py"), None, None),
                    "quux.py": File(("bar", "quux.py"), None, None),
                    "glarch.py": File(("bar", "glarch.py"), None, None),
                },
            ),
        },
    )


def test_get_package_tree_package_paths_conflict(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    create_file(tmp_path / "bar/__init__.py")
    create_file(tmp_path / "bar/quux.py")
    create_file(tmp_path / "bar/glarch.py")
    create_file(tmp_path / "src/bar/gnusto.py")
    monkeypatch.chdir(tmp_path)
    cfg = Configuration(package_paths=[Path("bar"), Path("src/bar")])
    with pytest.raises(UserInputError) as excinfo:
        cfg.get_package_tree()
    assert str(excinfo.value) == (
        f"`--package src{os.sep}bar` adds 'bar' to file tree, but it is already"
        " present from prior --package option"
    )


def test_get_package_tree_src_dirs_conflict(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    create_file(tmp_path / "source/bar/__init__.py")
    create_file(tmp_path / "source/bar/quux.py")
    create_file(tmp_path / "source/bar/glarch.py")
    create_file(tmp_path / "src/bar/gnusto.py")
    monkeypatch.chdir(tmp_path)
    cfg = Configuration(src_dirs=[Path("source"), Path("src")])
    with pytest.raises(UserInputError) as excinfo:
        cfg.get_package_tree()
    assert str(excinfo.value) == (
        "`--src-dir src` adds 'bar' to file tree, but it is already present"
        " from prior --package or --src-dir option"
    )


def test_get_package_tree_package_path_src_dir_conflict(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    create_file(tmp_path / "bar/__init__.py")
    create_file(tmp_path / "bar/quux.py")
    create_file(tmp_path / "bar/glarch.py")
    create_file(tmp_path / "src/bar/gnusto.py")
    monkeypatch.chdir(tmp_path)
    cfg = Configuration(package_paths=[Path("bar")], src_dirs=[Path("src")])
    with pytest.raises(UserInputError) as excinfo:
        cfg.get_package_tree()
    assert str(excinfo.value) == (
        "`--src-dir src` adds 'bar' to file tree, but it is already present"
        " from prior --package or --src-dir option"
    )


def test_toml_unicode(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.check-wheel-contents]\n"
        'select = "W001"\n'
        "\n"
        "[project]\n"
        'description = "Factory ⸻ A code generator 🏭"\n'
        'authors = [{name = "Łukasz Langa"}]\n',
        encoding="utf-8",
    )
    Configuration.from_file(tmp_path / "pyproject.toml")
