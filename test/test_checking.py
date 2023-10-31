from __future__ import annotations
from collections.abc import Callable, Iterable
import pytest
from check_wheel_contents.checker import COMMON_NAMES, WheelChecker
from check_wheel_contents.checks import Check, FailedCheck
from check_wheel_contents.contents import WheelContents
from check_wheel_contents.filetree import Directory, File

DUMMY_HASH = "sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk"
DUMMY_SIZE = "69105"


def wheel_from_paths(paths: Iterable[str]) -> WheelContents:
    whlcon = WheelContents(
        dist_info_dir="foo-1.0.dist-info",
        data_dir="foo-1.0.data",
        root_is_purelib=True,
    )
    whlcon.add_record_rows([[p, DUMMY_HASH, DUMMY_SIZE] for p in paths])
    whlcon.add_record_rows([["foo-1.0.dist-info/METADATA", DUMMY_HASH, DUMMY_SIZE]])
    whlcon.validate_tree()
    return whlcon


@pytest.mark.parametrize(
    "paths,failures",
    [
        (["foo.py"], []),
        (["foo.py", "foo.pyc"], [FailedCheck(Check.W001, ["foo.pyc"])]),
        (["foo.py", "foo.pyo"], [FailedCheck(Check.W001, ["foo.pyo"])]),
        (
            ["foo.py", "__pycache__/foo.cpython-36.pyc"],
            [FailedCheck(Check.W001, ["__pycache__/foo.cpython-36.pyc"])],
        ),
        (
            ["foo.py", "__pycache__/foo.cpython-36.opt-1.pyc"],
            [FailedCheck(Check.W001, ["__pycache__/foo.cpython-36.opt-1.pyc"])],
        ),
        (
            [
                "foo/__init__.py",
                "foo/bar.py",
                "foo/__pycache__/__init__.cpython-36.pyc",
                "foo/__pycache__/bar.cpython-36.pyc",
                "foo/subfoo/__init__.py",
                "foo/subfoo/__pycache__/__init__.cpython-36.pyc",
            ],
            [
                FailedCheck(
                    Check.W001,
                    [
                        "foo/__pycache__/__init__.cpython-36.pyc",
                        "foo/__pycache__/bar.cpython-36.pyc",
                        "foo/subfoo/__pycache__/__init__.cpython-36.pyc",
                    ],
                )
            ],
        ),
        (
            ["foo.py", "foo-1.0.dist-info/how-did-this-get-here.pyc"],
            [
                FailedCheck(
                    Check.W001,
                    ["foo-1.0.dist-info/how-did-this-get-here.pyc"],
                )
            ],
        ),
        (
            [
                "foo-1.0.data/platlib/foo.py",
                "foo-1.0.data/platlib/__pycache__/foo.cpython-36.pyc",
            ],
            [
                FailedCheck(
                    Check.W001, ["foo-1.0.data/platlib/__pycache__/foo.cpython-36.pyc"]
                )
            ],
        ),
        (
            [
                "foo-1.0.data/other/foo.py",
                "foo-1.0.data/other/__pycache__/foo.cpython-36.pyc",
            ],
            [
                FailedCheck(
                    Check.W001, ["foo-1.0.data/other/__pycache__/foo.cpython-36.pyc"]
                )
            ],
        ),
    ],
)
def test_check_W001(paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker()
    assert checker.check_W001(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize(
    "rows,failures",
    [
        (
            [
                [
                    "foo-1.0.dist-info/METADATA",
                    "sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk",
                    "950",
                ],
                [
                    "foo.py",
                    "sha256=UxbST6sF1RzAkvG8kCt15x13QBsB5FPeLnRJ4wHMqps",
                    "1003",
                ],
            ],
            [],
        ),
        (
            [
                [
                    "foo-1.0.dist-info/METADATA",
                    "sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk",
                    "950",
                ],
                [
                    "foo.py",
                    "sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4",
                    "995",
                ],
                [
                    "foo/__init__.py",
                    "sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU",
                    "0",
                ],
                [
                    "foo/duplicate.py",
                    "sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4",
                    "995",
                ],
            ],
            [FailedCheck(Check.W002, ["foo.py", "foo/duplicate.py"])],
        ),
        (
            [
                [
                    "foo-1.0.dist-info/METADATA",
                    "sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk",
                    "950",
                ],
                [
                    "foo/__init__.py",
                    "sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU",
                    "0",
                ],
                [
                    "foo/bar.py",
                    "sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4",
                    "995",
                ],
                [
                    "foo/baz/__init__.py",
                    "sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU",
                    "0",
                ],
                [
                    "foo/baz/glarch.py",
                    "sha256=m3wA6iovIgZaLZYr_xrE8iSsa_LuKNeaXihzIV4uyMk",
                    "973",
                ],
            ],
            [],
        ),
        (
            [
                [
                    "foo-1.0.dist-info/METADATA",
                    "sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk",
                    "950",
                ],
                [
                    "foo/__init__.py",
                    "sha256=iwhKnzeBJLKxpRVjvzwiRE63_zNpIBfaKLITauVph-0",
                    "24",
                ],
                [
                    "foo/bar.py",
                    "sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4",
                    "995",
                ],
                [
                    "foo/baz/__init__.py",
                    "sha256=iwhKnzeBJLKxpRVjvzwiRE63_zNpIBfaKLITauVph-0",
                    "24",
                ],
                [
                    "foo/baz/glarch.py",
                    "sha256=m3wA6iovIgZaLZYr_xrE8iSsa_LuKNeaXihzIV4uyMk",
                    "973",
                ],
            ],
            [],
        ),
        (
            [
                [
                    "foo-1.0.dist-info/METADATA",
                    "sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk",
                    "950",
                ],
                [
                    "foo.py",
                    "sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4",
                    "995",
                ],
                [
                    "foo/__init__.py",
                    "sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU",
                    "0",
                ],
                [
                    "foo/duplicate.py",
                    "sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4",
                    "995",
                ],
                [
                    "foo/bar.py",
                    "sha256=D43B5klhA1Tiklczo1UwVmIPeprAw3XTE5p4VdeJIHs",
                    "1007",
                ],
                [
                    "foo/another_duplicate.py",
                    "sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4",
                    "995",
                ],
            ],
            [
                FailedCheck(
                    Check.W002,
                    [
                        "foo.py",
                        "foo/duplicate.py",
                        "foo/another_duplicate.py",
                    ],
                )
            ],
        ),
        (
            [
                [
                    "foo-1.0.dist-info/METADATA",
                    "sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk",
                    "950",
                ],
                [
                    "foo-1.0.dist-info/LICENSE",
                    "sha256=oVov1f8LxBN1tMMdn93JEkqCNaMTunicL391TsKTYs8",
                    "1012",
                ],
                [
                    "foo-1.0.dist-info/NOTICE.txt",
                    "sha256=oVov1f8LxBN1tMMdn93JEkqCNaMTunicL391TsKTYs8",
                    "1012",
                ],
                [
                    "foo.py",
                    "sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4",
                    "995",
                ],
                [
                    "foo/__init__.py",
                    "sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU",
                    "0",
                ],
                [
                    "foo/duplicate.py",
                    "sha256=feFUDF3H45ZfOetuMteWVwEzHex4AH9o_1vuVTvl9g4",
                    "995",
                ],
            ],
            [
                FailedCheck(
                    Check.W002,
                    [
                        "foo-1.0.dist-info/LICENSE",
                        "foo-1.0.dist-info/NOTICE.txt",
                    ],
                ),
                FailedCheck(Check.W002, ["foo.py", "foo/duplicate.py"]),
            ],
        ),
        (
            [
                [
                    "foo-1.0.dist-info/METADATA",
                    "sha256=NVefY26xjCmYCQCnZaKUTNc5WaqZHDKxVde8l72cVOk",
                    "950",
                ],
                [
                    "foo/__init__.py",
                    "sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU",
                    "0",
                ],
                [
                    "foo/__main__.py",
                    "sha256=tQnRYEpcEVliJvvWU8Y4pAoe9rl1NqH6YJQuuPgXmtQ",
                    "1000",
                ],
                [
                    "foo-1.0.data/scripts/command",
                    "sha256=tQnRYEpcEVliJvvWU8Y4pAoe9rl1NqH6YJQuuPgXmtQ",
                    "1000",
                ],
            ],
            [
                FailedCheck(
                    Check.W002, ["foo/__main__.py", "foo-1.0.data/scripts/command"]
                )
            ],
        ),
    ],
)
def test_check_W002(rows: list[list[str]], failures: list[FailedCheck]) -> None:
    whlcon = WheelContents(
        dist_info_dir="foo-1.0.dist-info",
        data_dir="foo-1.0.data",
        root_is_purelib=True,
    )
    whlcon.add_record_rows(rows)
    whlcon.validate_tree()
    checker = WheelChecker()
    assert checker.check_W002(whlcon) == failures


@pytest.mark.parametrize(
    "paths,failures",
    [
        (["weirdo.txt/notpython.c"], []),
        (
            [
                "foo.pth",
                "foo.py",
                "foo.so",
                "foo.cpython-38-x86_64-linux-gnu.so",
                "foo.cpython-38-darwin.so",
                "foo.cp38-win_amd64.pyd",
                "foo.abi3.so",
            ],
            [],
        ),
        (
            [
                "foo-1.0.data/platlib/foo.pth",
                "foo-1.0.data/platlib/foo.py",
                "foo-1.0.data/platlib/foo.so",
                "foo-1.0.data/platlib/foo.cpython-38-x86_64-linux-gnu.so",
                "foo-1.0.data/platlib/foo.cpython-38-darwin.so",
                "foo-1.0.data/platlib/foo.cp38-win_amd64.pyd",
                "foo-1.0.data/platlib/foo.abi3.so",
            ],
            [],
        ),
        (["empty/"], []),
        (
            ["foo.PY", "foo.py", "foo.pyc", "foo.pyo"],
            [FailedCheck(Check.W003, ["foo.PY", "foo.pyc", "foo.pyo"])],
        ),
        (["bar/foo.PY", "bar/foo.py", "bar/foo.pyc", "bar/foo.pyo"], []),
        (
            [
                "foo-1.0.data/platlib/foo.PY",
                "foo-1.0.data/platlib/foo.py",
                "foo-1.0.data/platlib/foo.pyc",
                "foo-1.0.data/platlib/foo.pyo",
            ],
            [
                FailedCheck(
                    Check.W003,
                    [
                        "foo-1.0.data/platlib/foo.PY",
                        "foo-1.0.data/platlib/foo.pyc",
                        "foo-1.0.data/platlib/foo.pyo",
                    ],
                )
            ],
        ),
        (
            ["README.rst", "METADATA", "empty"],
            [FailedCheck(Check.W003, ["README.rst", "METADATA", "empty"])],
        ),
        (
            [
                "foo-1.0.data/platlib/README.rst",
                "foo-1.0.data/platlib/METADATA",
                "foo-1.0.data/platlib/empty",
            ],
            [
                FailedCheck(
                    Check.W003,
                    [
                        "foo-1.0.data/platlib/README.rst",
                        "foo-1.0.data/platlib/METADATA",
                        "foo-1.0.data/platlib/empty",
                    ],
                )
            ],
        ),
        (
            [
                "foo-1.0.dist-info/README.rst",
                "foo-1.0.dist-info/METADATA2",
                "foo-1.0.dist-info/empty",
            ],
            [],
        ),
        (
            [
                "foo-1.0.data/scripts/README.rst",
                "foo-1.0.data/scripts/METADATA",
                "foo-1.0.data/scripts/empty",
            ],
            [],
        ),
    ],
)
def test_check_W003(paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker()
    assert checker.check_W003(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize(
    "paths,failures",
    [
        (
            [
                "foo.py",
                "def.py",
                "has-hyphen.py",
                "extra.ext.py",
                "bar/__init__.py",
                "bar/is.py",
                "bar/hyphen-ated.py",
                "bar/glarch.quux.py",
                "with/foo.py",
                "in-dir/foo.py",
                "in.pkg/foo.py",
            ],
            [
                FailedCheck(
                    Check.W004,
                    [
                        "def.py",
                        "has-hyphen.py",
                        "extra.ext.py",
                        "bar/is.py",
                        "bar/hyphen-ated.py",
                        "bar/glarch.quux.py",
                        "with/foo.py",
                        "in-dir/foo.py",
                        "in.pkg/foo.py",
                    ],
                ),
            ],
        ),
        (
            [
                "foo-1.0.data/platlib/foo.py",
                "foo-1.0.data/platlib/def.py",
                "foo-1.0.data/platlib/has-hyphen.py",
                "foo-1.0.data/platlib/extra.ext.py",
                "foo-1.0.data/platlib/bar/__init__.py",
                "foo-1.0.data/platlib/bar/is.py",
                "foo-1.0.data/platlib/bar/hyphen-ated.py",
                "foo-1.0.data/platlib/bar/glarch.quux.py",
                "foo-1.0.data/platlib/with/foo.py",
                "foo-1.0.data/platlib/in-dir/foo.py",
                "foo-1.0.data/platlib/in.pkg/foo.py",
            ],
            [
                FailedCheck(
                    Check.W004,
                    [
                        "foo-1.0.data/platlib/def.py",
                        "foo-1.0.data/platlib/has-hyphen.py",
                        "foo-1.0.data/platlib/extra.ext.py",
                        "foo-1.0.data/platlib/bar/is.py",
                        "foo-1.0.data/platlib/bar/hyphen-ated.py",
                        "foo-1.0.data/platlib/bar/glarch.quux.py",
                        "foo-1.0.data/platlib/with/foo.py",
                        "foo-1.0.data/platlib/in-dir/foo.py",
                        "foo-1.0.data/platlib/in.pkg/foo.py",
                    ],
                ),
            ],
        ),
        (
            [
                "foo-1.0.data/scripts/foo.py",
                "foo-1.0.data/scripts/def.py",
                "foo-1.0.data/scripts/has-hyphen.py",
                "foo-1.0.data/scripts/extra.ext.py",
                "foo-1.0.data/scripts/bar/__init__.py",
                "foo-1.0.data/scripts/bar/is.py",
                "foo-1.0.data/scripts/bar/hyphen-ated.py",
                "foo-1.0.data/scripts/bar/glarch.quux.py",
                "foo-1.0.data/scripts/with/foo.py",
                "foo-1.0.data/scripts/in-dir/foo.py",
                "foo-1.0.data/scripts/in.pkg/foo.py",
            ],
            [],
        ),
    ],
)
def test_check_W004(paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker()
    assert checker.check_W004(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize("name", COMMON_NAMES)
@pytest.mark.parametrize(
    "paths,failures",
    [
        pytest.param(
            ["{}/foo.py", "not_{}/foo.py", "{}.py"],
            [FailedCheck(Check.W005, ["{}/"])],
            id="root",
        ),
        pytest.param(["quux/{}/foo.py"], [], id="nested"),
        pytest.param(["{}"], [FailedCheck(Check.W005, ["{}"])], id="root_dir"),
        pytest.param(
            ["foo-1.0.data/platlib/{}/foo.py"],
            [FailedCheck(Check.W005, ["foo-1.0.data/platlib/{}/"])],
            id="deeply_nested",
        ),
        pytest.param(["foo-1.0.data/scripts/{}/foo.py"], [], id="data"),
    ],
)
def test_check_W005(name: str, paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker()
    failures = [
        FailedCheck(f.check, [a.format(name) for a in f.args]) for f in failures
    ]
    assert (
        checker.check_W005(wheel_from_paths(p.format(name) for p in paths)) == failures
    )


@pytest.mark.parametrize("name", COMMON_NAMES)
@pytest.mark.parametrize(
    "paths",
    [
        pytest.param(["{}/foo.py", "not_{}/foo.py", "{}.py"], id="root"),
        pytest.param(["quux/{}/foo.py"], id="nested"),
        pytest.param(["{}"], id="root_dir"),
        pytest.param(["foo-1.0.data/platlib/{}/foo.py"], id="deeply_nested"),
        pytest.param(["foo-1.0.data/scripts/{}/foo.py"], id="data"),
    ],
)
def test_check_W005_exclude_toplevel(name: str, paths: list[str]) -> None:
    checker = WheelChecker(toplevel=[name])
    failures = checker.check_W005(wheel_from_paths(p.format(name) for p in paths))
    assert not failures


@pytest.mark.parametrize(
    "paths,failures",
    [
        (["__init__.py"], [FailedCheck(Check.W006, ["__init__.py"])]),
        (["foo/__init__.py"], []),
        (
            ["foo-1.0.data/platlib/__init__.py"],
            [FailedCheck(Check.W006, ["foo-1.0.data/platlib/__init__.py"])],
        ),
        (["foo-1.0.dist-info/__init__.py"], []),
        (["foo-1.0.data/scripts/__init__.py"], []),
    ],
)
def test_check_W006(paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker()
    assert checker.check_W006(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize(
    "paths,failures",
    [
        ([], [FailedCheck(Check.W007)]),
        (["foo.py"], []),
        (["foo-1.0.data/platlib/foo.py"], []),
        (["foo-1.0.data/platlib/"], [FailedCheck(Check.W007)]),
        (["foo-1.0.data/scripts/foo.py"], [FailedCheck(Check.W007)]),
    ],
)
def test_check_W007(paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker()
    assert checker.check_W007(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize(
    "paths,failures",
    [
        ([], [FailedCheck(Check.W008)]),
        (["foo.py"], []),
        (["foo-1.0.data/platlib/foo.py"], []),
        (["foo-1.0.data/platlib/"], []),
        (["foo-1.0.data/scripts/foo.py"], []),
        (["foo-1.0.dist-info/foo.py"], [FailedCheck(Check.W008)]),
    ],
)
def test_check_W008(paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker()
    assert checker.check_W008(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize(
    "paths,failures",
    [
        (["foo.py", "bar/__init__.py"], [FailedCheck(Check.W009, ["foo.py", "bar/"])]),
        (
            ["foo.py", "foo-1.0.data/platlib/bar/__init__.py"],
            [FailedCheck(Check.W009, ["foo.py", "foo-1.0.data/platlib/bar/"])],
        ),
        (
            ["foo.py", "bar/nonpython.txt"],
            [FailedCheck(Check.W009, ["foo.py", "bar/"])],
        ),
        (["foo.py", "_bar/__init__.py"], []),
        (["foo.py", "bar.pth"], []),
        (["foo.py", "bar.rst"], [FailedCheck(Check.W009, ["foo.py", "bar.rst"])]),
        (["_foo.py", "foo-1.0.data/platlib/bar.py"], []),
    ],
)
def test_check_W009(paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker()
    assert checker.check_W009(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize(
    "paths",
    [
        ["foo.py", "bar/__init__.py"],
        ["foo.py", "baz/__init__.py"],
        ["foo.py", "foo-1.0.data/platlib/bar/__init__.py"],
        ["foo.py", "bar/nonpython.txt"],
        ["foo.py", "_bar/__init__.py"],
        ["foo.py", "bar.pth"],
        ["foo.py", "bar.rst"],
        ["_foo.py", "foo-1.0.data/platlib/bar.py"],
    ],
)
def test_check_W009_toplevel_set(paths: list[str]) -> None:
    checker = WheelChecker()
    checker.configure_options(toplevel=["foo.py", "bar"])
    assert checker.check_W009(wheel_from_paths(paths)) == []


@pytest.mark.parametrize(
    "paths",
    [
        ["foo.py", "bar/__init__.py"],
        ["foo.py", "baz/__init__.py"],
        ["foo.py", "foo-1.0.data/platlib/bar/__init__.py"],
        ["foo.py", "bar/nonpython.txt"],
        ["foo.py", "_bar/__init__.py"],
        ["foo.py", "bar.pth"],
        ["foo.py", "bar.rst"],
        ["_foo.py", "foo-1.0.data/platlib/bar.py"],
    ],
)
def test_check_W009_pkgtree_set(paths: list[str]) -> None:
    checker = WheelChecker(pkgtree=Directory())
    assert checker.check_W009(wheel_from_paths(paths)) == []


@pytest.mark.parametrize(
    "paths,failures",
    [
        (["foo/README.txt"], [FailedCheck(Check.W010, ["foo/"])]),
        (
            ["foo-1.0.data/platlib/foo/README.txt"],
            [FailedCheck(Check.W010, ["foo-1.0.data/platlib/foo/"])],
        ),
        (["foo-1.0.data/data/foo/README.txt"], []),
        (["foo.txt"], []),
        (["foo/foo.txt", "foo/__init__.py", "foo/bar/data.dat"], []),
        (["foo/bar/"], [FailedCheck(Check.W010, ["foo/"])]),
        (["foo/bar.pyi"], [FailedCheck(Check.W010, ["foo/"])]),
        (["foo-stubs/bar.pyi"], []),
        (["-stubs/bar.pyi"], [FailedCheck(Check.W010, ["-stubs/"])]),
    ],
)
def test_check_W010(paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker()
    assert checker.check_W010(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize(
    "paths",
    [
        ["foo.py", "bar/__init__.py"],
        ["foo.py", "baz/__init__.py"],
        ["foo.py", "foo-1.0.data/platlib/bar/__init__.py"],
        ["foo.py", "bar/nonpython.txt"],
        ["foo.py", "_bar/__init__.py"],
        ["foo.py", "bar.pth"],
        ["foo.py", "bar.rst"],
        ["_foo.py", "foo-1.0.data/platlib/bar.py"],
    ],
)
@pytest.mark.parametrize(
    "check_method",
    [
        WheelChecker.check_W101,
        WheelChecker.check_W102,
    ],
)
def test_check_W1_pkgtree_not_set(
    paths: list[str],
    check_method: Callable[[WheelChecker, WheelContents], list[FailedCheck]],
) -> None:
    checker = WheelChecker()
    assert check_method(checker, wheel_from_paths(paths)) == []


@pytest.mark.parametrize(
    "paths,failures",
    [
        (["foo.py", "bar/__init__.py", "bar/bar.py", "bar/empty/"], []),
        (["foo.py", "bar/__init__.py", "bar/bar.py"], []),
        (["foo.py", "bar/__init__.py", "bar/bar.py", "extra.py"], []),
        (
            [
                "bar/__init__.py",
                "bar/bar.py",
            ],
            [FailedCheck(Check.W101, ["foo.py"])],
        ),
        (["foo.py"], [FailedCheck(Check.W101, ["bar/__init__.py", "bar/bar.py"])]),
        (
            [
                "foo.py",
                "foo-1.0.data/platlib/bar/__init__.py",
                "foo-1.0.data/platlib/bar/bar.py",
            ],
            [],
        ),
        (["foo.py", "bar/__init__.py", "foo-1.0.data/platlib/bar/bar.py"], []),
        (
            [
                "foo-1.0.data/platlib/foo.py",
                "foo-1.0.data/platlib/bar/__init__.py",
                "foo-1.0.data/platlib/bar/bar.py",
            ],
            [],
        ),
    ],
)
def test_check_W101(paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker(
        pkgtree=Directory(
            path=None,
            entries={
                "foo.py": File(("foo.py",), None, None),
                "bar": Directory(
                    path="bar/",
                    entries={
                        "__init__.py": File(("bar", "__init__.py"), None, None),
                        "bar.py": File(("bar", "bar.py"), None, None),
                        "empty": Directory(path="bar/empty/"),
                    },
                ),
            },
        ),
    )
    assert checker.check_W101(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize(
    "paths,failures",
    [
        (["foo.py", "bar/__init__.py", "bar/bar.py", "bar/empty/"], []),
        (["foo.py", "bar/__init__.py", "bar/bar.py", "empty/"], []),
        (
            ["foo.py", "bar/__init__.py", "bar/bar.py", "quux.py"],
            [FailedCheck(Check.W102, ["quux.py"])],
        ),
        (
            ["foo.py", "bar/__init__.py", "bar/bar.py", "bar/quux.py"],
            [FailedCheck(Check.W102, ["bar/quux.py"])],
        ),
        (
            ["foo.py", "bar/__init__.py", "bar/bar.py", "foo-1.0.data/platlib/quux.py"],
            [FailedCheck(Check.W102, ["foo-1.0.data/platlib/quux.py"])],
        ),
        (
            ["foo.py", "bar/__init__.py", "bar/bar.py", "foo.pyc"],
            [FailedCheck(Check.W102, ["foo.pyc"])],
        ),
        (["foo.py", "foo-1.0.data/scripts/quux.py"], []),
        (["foo.py", "foo-1.0.dist-info/quux.py"], []),
    ],
)
def test_check_W102(paths: list[str], failures: list[FailedCheck]) -> None:
    checker = WheelChecker(
        pkgtree=Directory(
            path=None,
            entries={
                "foo.py": File(("foo.py",), None, None),
                "bar": Directory(
                    path="bar/",
                    entries={
                        "__init__.py": File(("bar", "__init__.py"), None, None),
                        "bar.py": File(("bar", "bar.py"), None, None),
                        "empty": Directory(path="bar/empty/"),
                    },
                ),
            },
        ),
    )
    assert checker.check_W102(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize(
    "paths",
    [
        ["foo.py", "bar/__init__.py"],
        ["foo.py", "baz/__init__.py"],
        ["foo.py", "foo-1.0.data/platlib/bar/__init__.py"],
        ["foo.py", "bar/nonpython.txt"],
        ["foo.py", "_bar/__init__.py"],
        ["foo.py", "bar.pth"],
        ["foo.py", "bar.rst"],
        ["_foo.py", "foo-1.0.data/platlib/bar.py"],
    ],
)
@pytest.mark.parametrize(
    "check_method", [WheelChecker.check_W201, WheelChecker.check_W202]
)
def test_check_W2_toplevel_not_set(
    paths: list[str],
    check_method: Callable[[WheelChecker, WheelContents], list[FailedCheck]],
) -> None:
    checker = WheelChecker()
    assert check_method(checker, wheel_from_paths(paths)) == []


@pytest.mark.parametrize(
    "paths,failures",
    [
        (["foo.py", "bar/__init__.py"], []),
        (["bar/__init__.py", "foo.py"], []),
        (["foo/__init__.py", "bar/__init__.py"], [FailedCheck(Check.W201, ["foo.py"])]),
        (["foo.py", "bar.py"], [FailedCheck(Check.W201, ["bar"])]),
        (["foo.py"], [FailedCheck(Check.W201, ["bar"])]),
        (["bar/__init__.py"], [FailedCheck(Check.W201, ["foo.py"])]),
        (["foo.py", "baz/__init__.py"], [FailedCheck(Check.W201, ["bar"])]),
        (["foo.py", "bar/__init__.py", "glarch/__init__.py"], []),
        (
            ["foo.py", "foo-1.0.data/platlib/bar/__init__.py"],
            [],
        ),
        (
            [
                "foo-1.0.data/platlib/foo.py",
                "foo-1.0.data/platlib/bar/__init__.py",
            ],
            [],
        ),
        (["foo.py", "bar"], []),
        (
            ["foo-1.0.data/scripts/foo.py", "bar/__init__.py"],
            [FailedCheck(Check.W201, ["foo.py"])],
        ),
        ([], [FailedCheck(Check.W201, ["foo.py", "bar"])]),
        (["foo.py", "bar/__init__.py", "quux.pth"], []),
        (["foo.py", "bar/__init__.py", "_glarch.py"], []),
    ],
)
@pytest.mark.parametrize("toplevel", [["foo.py", "bar"], ["foo.py", "bar/"]])
def test_check_W201(
    paths: list[str], failures: list[FailedCheck], toplevel: list[str]
) -> None:
    checker = WheelChecker()
    checker.configure_options(toplevel=toplevel)
    assert checker.check_W201(wheel_from_paths(paths)) == failures


@pytest.mark.parametrize(
    "paths,failures",
    [
        (["foo.py", "bar/__init__.py"], []),
        (["bar/__init__.py", "foo.py"], []),
        (["foo/__init__.py", "bar/__init__.py"], [FailedCheck(Check.W202, ["foo/"])]),
        (["foo.py", "bar.py"], [FailedCheck(Check.W202, ["bar.py"])]),
        (["foo.py"], []),
        (["bar/__init__.py"], []),
        (["foo.py", "baz/__init__.py"], [FailedCheck(Check.W202, ["baz/"])]),
        (
            ["foo.py", "bar/__init__.py", "glarch/__init__.py"],
            [FailedCheck(Check.W202, ["glarch/"])],
        ),
        (["foo.py", "foo-1.0.data/platlib/bar/__init__.py"], []),
        (
            [
                "foo-1.0.data/platlib/foo.py",
                "foo-1.0.data/platlib/bar/__init__.py",
            ],
            [],
        ),
        (["foo.py", "bar"], []),
        (["foo-1.0.data/scripts/foo.py", "bar/__init__.py"], []),
        ([], []),
        (["foo.py", "bar/__init__.py", "quux.pth"], []),
        (
            ["foo.py", "bar/__init__.py", "_glarch.py"],
            [FailedCheck(Check.W202, ["_glarch.py"])],
        ),
        (
            ["foo.py", "bar/__init__.py", "data.dat"],
            [FailedCheck(Check.W202, ["data.dat"])],
        ),
        (
            ["foo.py", "bar/__init__.py", "empty/"],
            [FailedCheck(Check.W202, ["empty/"])],
        ),
        (["foo/__init__.py", "bar.py"], [FailedCheck(Check.W202, ["foo/", "bar.py"])]),
    ],
)
@pytest.mark.parametrize("toplevel", [["foo.py", "bar"], ["foo.py", "bar/"]])
def test_check_W202(
    paths: list[str], failures: list[FailedCheck], toplevel: list[str]
) -> None:
    checker = WheelChecker()
    checker.configure_options(toplevel=toplevel)
    assert checker.check_W202(wheel_from_paths(paths)) == failures
