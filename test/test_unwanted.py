from __future__ import annotations
import base64
import csv
import hashlib
from io import StringIO
from pathlib import Path
import stat
from zipfile import ZipFile, ZipInfo
from click.testing import CliRunner
import pytest
from check_wheel_contents.__main__ import main
from check_wheel_contents.checker import WheelChecker
from check_wheel_contents.config import Configuration
from check_wheel_contents.contents import WheelContents

CACHE_TAG = b"Signature: 8a477f597d28d172789f06886806bc55"


def make_wheel(
    tmp_path: Path, files: dict[str, bytes], *, symlink_tag: bool = False
) -> Path:
    files = {
        "sample/__init__.py": b'"""Sample package."""\n',
        "sample-1.0.dist-info/WHEEL": (
            b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        ),
        "sample-1.0.dist-info/METADATA": (
            b"Metadata-Version: 2.1\nName: sample\nVersion: 1.0\n"
        ),
        **files,
    }
    record = StringIO()
    writer = csv.writer(record, lineterminator="\n")
    for path, data in files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
        writer.writerow([path, "sha256=" + digest.decode("ascii"), len(data)])
    record_path = "sample-1.0.dist-info/RECORD"
    writer.writerow([record_path, "", ""])
    wheel = tmp_path / "sample-1.0-py3-none-any.whl"
    with ZipFile(wheel, "w") as zf:
        for path, data in files.items():
            if symlink_tag and path.endswith("/CACHEDIR.TAG"):
                info = ZipInfo(path)
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                zf.writestr(info, data)
            else:
                zf.writestr(path, data)
        zf.writestr(record_path, record.getvalue())
    return wheel


def unwanted_paths(wheel: Path) -> list[str]:
    return [
        path
        for failure in WheelChecker().check_contents(WheelContents.from_wheel(wheel))
        if failure.check.name == "W011"
        for path in failure.args
    ]


@pytest.mark.parametrize(
    "path,expected",
    [
        ("sample/.module.py.swp", "sample/.module.py.swp"),
        ("sample/module.py~", "sample/module.py~"),
        ("sample/.#module.py", "sample/.#module.py"),
        ("sample/.module.py.un~", "sample/.module.py.un~"),
        ("sample/module.py.bak", "sample/module.py.bak"),
        ("sample/.DS_Store", "sample/.DS_Store"),
        ("sample/._module.py", "sample/._module.py"),
        ("sample/Thumbs.db", "sample/Thumbs.db"),
        ("sample/.coverage", "sample/.coverage"),
        ("sample/.coverage.host.123", "sample/.coverage.host.123"),
        ("sample/.mypy_cache/stale.json", "sample/.mypy_cache/"),
        ("__MACOSX/sample/resource", "__MACOSX/"),
        ("sample/.mypy_cache/", "sample/.mypy_cache/"),
        ("sample-1.0.data/scripts/editor~", "sample-1.0.data/scripts/editor~"),
        ("sample-1.0.dist-info/Thumbs.db", "sample-1.0.dist-info/Thumbs.db"),
    ],
)
def test_unwanted_artifacts(tmp_path: Path, path: str, expected: str) -> None:
    assert unwanted_paths(make_wheel(tmp_path, {path: b"artifact"})) == [expected]


@pytest.mark.parametrize(
    "path",
    [
        "sample/.gitignore",
        "sample/.config.json",
        "sample/.coveragerc",
        "sample/.module.swp.txt",
        "sample/module.bak.txt",
        "sample/thumbs.db",
        "sample/.mypy_cache_data/keep.txt",
        "sample/__MACOSX_data/keep.txt",
        "sample/.mypy_cache",
        "sample/__MACOSX",
    ],
)
def test_other_hidden_files_and_similar_names_are_allowed(
    tmp_path: Path, path: str
) -> None:
    assert (
        unwanted_paths(make_wheel(tmp_path, {path: b"intentional package data"})) == []
    )


@pytest.mark.parametrize("suffix", [b"", b"\n# generated cache\n", b"\r\n"])
def test_valid_cache_directory(tmp_path: Path, suffix: bytes) -> None:
    wheel = make_wheel(
        tmp_path,
        {
            "sample/cache/CACHEDIR.TAG": CACHE_TAG + suffix,
            "sample/cache/nested/keep.bin": b"regenerable cache data",
            "sample/cache/nested/.DS_Store": b"nested artifact",
        },
    )
    assert unwanted_paths(wheel) == ["sample/cache/"]


@pytest.mark.parametrize(
    "tag",
    [b"", CACHE_TAG[:-1], b"\n" + CACHE_TAG, CACHE_TAG.lower(), b"unrelated data"],
)
def test_invalid_cache_tag_preserves_directory(tmp_path: Path, tag: bytes) -> None:
    wheel = make_wheel(
        tmp_path,
        {"sample/cache/CACHEDIR.TAG": tag, "sample/cache/keep.bin": b"package data"},
    )
    assert unwanted_paths(wheel) == []


def test_symbolic_link_cache_tag_preserves_directory(tmp_path: Path) -> None:
    wheel = make_wheel(
        tmp_path,
        {"sample/cache/CACHEDIR.TAG": CACHE_TAG},
        symlink_tag=True,
    )
    assert unwanted_paths(wheel) == []


def test_root_cache_tag(tmp_path: Path) -> None:
    assert unwanted_paths(make_wheel(tmp_path, {"CACHEDIR.TAG": CACHE_TAG})) == [
        "CACHEDIR.TAG"
    ]


def test_cli_selection_and_ignoring(tmp_path: Path) -> None:
    wheel = make_wheel(tmp_path, {"sample/editor~": b"backup data"})
    runner = CliRunner()
    selected = runner.invoke(main, ["--no-config", "--select", "W011", str(wheel)])
    assert selected.exit_code == 1, selected.output
    assert "W011: Wheel contains unwanted files" in selected.output
    assert "sample/editor~" in selected.output
    ignored = runner.invoke(main, ["--no-config", "--ignore", "W011", str(wheel)])
    assert ignored.exit_code == 0, ignored.output
    assert ignored.output.endswith(": OK\n")


@pytest.mark.parametrize("option", ["package", "src_dir"])
@pytest.mark.parametrize("custom_omit", [None, [], ["keep.txt"]])
def test_default_source_exclusions(
    tmp_path: Path, option: str, custom_omit: list[str] | None
) -> None:
    package = tmp_path / "sample"
    package.mkdir()
    for name in ["keep.txt", "editor~", "editor.bak", "Thumbs.db"]:
        (package / name).write_text(name)
    (package / "__MACOSX").mkdir()
    (package / "__MACOSX" / "metadata").write_text("metadata")
    (package / "cache").mkdir()
    (package / "cache" / "CACHEDIR.TAG").write_bytes(CACHE_TAG)
    (package / "cache" / "data").write_text("cached")
    cfg = Configuration.model_validate({option: [package], "package_omit": custom_omit})
    tree = cfg.get_package_tree()
    assert tree is not None
    prefix = "sample/" if option == "package" else ""
    paths = {f.path for f in tree.all_files()}
    if custom_omit is None:
        assert paths == {prefix + "keep.txt"}
    else:
        expected = {
            prefix + name
            for name in [
                "keep.txt",
                "editor~",
                "editor.bak",
                "Thumbs.db",
                "__MACOSX/metadata",
                "cache/CACHEDIR.TAG",
                "cache/data",
            ]
        }
        if custom_omit:
            expected.remove(prefix + "keep.txt")
        assert paths == expected


@pytest.mark.parametrize(
    "tag", [b"", CACHE_TAG[:-1], b"\n" + CACHE_TAG, CACHE_TAG.lower()]
)
def test_invalid_local_cache_tag_preserves_source(tmp_path: Path, tag: bytes) -> None:
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "CACHEDIR.TAG").write_bytes(tag)
    (cache / "keep.txt").touch()
    tree = Configuration(src_dirs=[tmp_path]).get_package_tree()
    assert tree is not None
    assert {f.path for f in tree.all_files()} == {
        "cache/CACHEDIR.TAG",
        "cache/keep.txt",
    }


def test_local_symbolic_links_do_not_mark_cache(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "CACHEDIR.TAG").write_bytes(CACHE_TAG)
    (target / "keep.txt").touch()
    source = tmp_path / "source"
    source.mkdir()
    (source / "directory-link").symlink_to(target, target_is_directory=True)
    (source / "marker-link").mkdir()
    (source / "marker-link" / "CACHEDIR.TAG").symlink_to(target / "CACHEDIR.TAG")
    (source / "marker-link" / "keep.txt").touch()
    tree = Configuration(src_dirs=[source]).get_package_tree()
    assert tree is not None
    assert {f.path for f in tree.all_files()} == {
        "directory-link/CACHEDIR.TAG",
        "directory-link/keep.txt",
        "marker-link/CACHEDIR.TAG",
        "marker-link/keep.txt",
    }


@pytest.mark.parametrize("config_format", ["toml", "ini"])
def test_cli_source_exclusion_defaults_can_be_overridden(
    tmp_path: Path, config_format: str
) -> None:
    source = tmp_path / "src" / "sample"
    source.mkdir(parents=True)
    (source / "__init__.py").write_text('"""Sample package."""\n')
    (source / "editor~").write_text("backup")
    cache = source / "cache"
    cache.mkdir()
    (cache / "CACHEDIR.TAG").write_bytes(CACHE_TAG)
    (cache / "data").write_text("cached")
    wheel = make_wheel(tmp_path, {})
    runner = CliRunner()
    default = runner.invoke(
        main,
        [
            "--no-config",
            "--select",
            "W101,W102",
            "--src-dir",
            str(source.parent),
            str(wheel),
        ],
    )
    assert default.exit_code == 0, default.output
    cfg = tmp_path / ("pyproject.toml" if config_format == "toml" else "custom.ini")
    if config_format == "toml":
        cfg.write_text(
            '[tool.check-wheel-contents]\nsrc_dir = ["src"]\npackage_omit = []\n'
        )
    else:
        cfg.write_text("[check-wheel-contents]\nsrc_dir = src\npackage_omit =\n")
    custom = runner.invoke(
        main, ["--config", str(cfg), "--select", "W101,W102", str(wheel)]
    )
    assert custom.exit_code == 1, custom.output
    assert "W101" in custom.output
    assert "sample/editor~" in custom.output
    assert "sample/cache/data" in custom.output
    assert "sample/cache/CACHEDIR.TAG" in custom.output


def test_cache_tag_at_explicit_source_root_does_not_hide_selection(
    tmp_path: Path,
) -> None:
    source = tmp_path / "sample"
    source.mkdir()
    (source / "CACHEDIR.TAG").write_bytes(CACHE_TAG)
    (source / "keep.txt").touch()
    tree = Configuration(package_paths=[source]).get_package_tree()
    assert tree is not None
    assert {f.path for f in tree.all_files()} == {
        "sample/CACHEDIR.TAG",
        "sample/keep.txt",
    }
