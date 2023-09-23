from __future__ import annotations
from collections.abc import Sequence
from configparser import ConfigParser
from pathlib import Path
import sys
from typing import Any, List, Optional, Set
from pydantic import BaseModel, Field, ValidationError, field_validator
from .checks import Check, parse_check_prefix
from .errors import UserInputError
from .filetree import Directory
from .util import comma_split

if sys.version_info[:2] >= (3, 11):
    from tomllib import load as toml_load
else:
    from tomli import load as toml_load

#: The filenames that configuration is read from by default, in descending
#: order of preference
CONFIG_FILES = [
    "pyproject.toml",
    "tox.ini",
    "setup.cfg",
    "check-wheel-contents.cfg",
    ".check-wheel-contents.cfg",
]

#: The name of the configuration section from which the configuration is
#: retrieved for most configuration formats
CONFIG_SECTION = "check-wheel-contents"

#: The default set of exclusion patterns for traversing ``--package`` and
#: ``--src-dir`` directories
TRAVERSAL_EXCLUSIONS = [".*", "CVS", "RCS", "*.pyc", "*.pyo", "*.egg-info"]


class Configuration(BaseModel, populate_by_name=True):
    """A container for a `WheelChecker`'s raw configuration values"""

    #: The set of selected checks, or `None` if not specified
    select: Optional[Set[Check]] = None
    #: The set of ignored checks, or `None` if not specified
    ignore: Optional[Set[Check]] = None
    #: The list of toplevel names to check for with the W2 checks, or `None` if
    #: not specified
    toplevel: Optional[List[str]] = None
    #: The list of paths specified with ``--package``, or `None` if not
    #: specified
    package_paths: Optional[List[Path]] = Field(None, alias="package")
    #: The list of paths specified with ``--src-dir``, or `None` if not
    #: specified
    src_dirs: Optional[List[Path]] = Field(None, alias="src_dir")
    #: The set of exclusion patterns for traversing ``package_paths`` and
    #: ``src_dirs``, or `None` if not specified
    package_omit: Optional[List[str]] = None

    @field_validator("select", "ignore", mode="before")
    @classmethod
    def _convert_check_set(cls, value: Any) -> Any:
        """
        If the input is a sequence, convert it to a `set` with any strings
        converted from check names & check name prefixes to `Check` objects.
        """
        if isinstance(value, Sequence):
            checks = set()
            for c in value:
                if isinstance(c, str):
                    checks |= parse_check_prefix(c)
                else:
                    checks.add(c)
            return checks
        else:
            return value

    @field_validator(
        "select",
        "ignore",
        "toplevel",
        "package_paths",
        "src_dirs",
        "package_omit",
        mode="before",
    )
    @classmethod
    def _convert_comma_list(cls, value: Any) -> Any:
        """
        Convert strings to lists by splitting on commas.  Leave everything else
        untouched.
        """
        if isinstance(value, str):
            return comma_split(value)
        else:
            return value

    @field_validator("toplevel")
    @classmethod
    def _convert_toplevel(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        """
        Strip trailing forward slashes from the elements of a list, if defined
        """
        if value is not None:
            value = [tl.rstrip("/") for tl in value]
        return value

    @classmethod
    def from_command_options(
        cls,
        select: Optional[set[Check]] = None,
        ignore: Optional[set[Check]] = None,
        toplevel: Optional[list[str]] = None,
        package: tuple[str, ...] = (),
        src_dir: tuple[str, ...] = (),
        package_omit: Optional[list[str]] = None,
    ) -> Configuration:
        """
        Construct a `Configuration` instance from option values passed in on
        the command line.  If either ``package`` or ``src_dir`` is an empty
        tuple (indicating that the corresponding option was not given on the
        command line), it is replaced by `None`.
        """
        return cls(
            select=select,
            ignore=ignore,
            toplevel=toplevel,
            package_paths=package or None,
            src_dirs=src_dir or None,
            package_omit=package_omit,
        )

    @classmethod
    def from_config_file(cls, path: Optional[str] = None) -> Configuration:
        """
        Construct a `Configuration` instance from the configuration file at the
        given path.  If the path is `None`, read from the default configuration
        file.  If the read configuration file does not contain the appropriate
        section, or if the default configuration file is not found, return a
        `Configuration` instance with all-default values.
        """
        if path is None:
            cfg = cls.find_default()
        else:
            cfg = cls.from_file(Path(path))
        if cfg is None:
            return cls()
        else:
            return cfg

    @classmethod
    def find_default(cls) -> Optional["Configuration"]:
        """
        Find the default configuration file and read the relevant section from
        it.  Returns `None` if no file with the appropriate section is found.
        """
        cwd = Path()
        for d in (cwd, *cwd.resolve().parents):
            found = [d / cf for cf in CONFIG_FILES if (d / cf).exists()]
            if found:
                for p in found:
                    cfg = cls.from_file(p)
                    if cfg is not None:
                        return cfg
                return None
        return None

    @classmethod
    def from_file(cls, path: Path) -> Optional["Configuration"]:
        """
        Read the relevant section from the given configuration file.  Returns
        `None` if the section does not exist.
        """
        if path.suffix == ".toml":
            with path.open("rb") as fb:
                tdata = toml_load(fb)
            tool = tdata.get("tool")
            if not isinstance(tool, dict):
                return None
            cfg = tool.get(CONFIG_SECTION)
            if cfg is None:
                return None
            else:
                try:
                    config = cls.model_validate(cfg)
                    config.resolve_paths(path)
                except (UserInputError, ValidationError) as e:
                    raise UserInputError(f"{path}: {e}")
                return config
        else:
            cdata = ConfigParser()
            with path.open(encoding="utf-8") as fp:
                cdata.read_file(fp)
            if path.name == "setup.cfg":
                section = f"tool:{CONFIG_SECTION}"
            else:
                section = CONFIG_SECTION
            if cdata.has_section(section):
                try:
                    config = cls.model_validate(cdata[section])
                    config.resolve_paths(path)
                except (UserInputError, ValidationError) as e:
                    raise UserInputError(f"{path}: {e}")
                return config
            else:
                return None

    def resolve_paths(self, configpath: Path) -> None:
        """
        Resolve the paths in ``package_paths`` and ``src_dirs`` relative to the
        directory containing ``configpath``.  If a resulting path does not
        exist (or, for ``src_dirs``, if it is not a directory), a
        `UserInputError` is raised.
        """
        base = configpath.resolve().parent
        if self.package_paths is not None:
            packages: list[Path] = []
            for p in self.package_paths:
                q = base / p
                if not q.exists():
                    raise UserInputError(
                        f"package: no such file or directory: {str(q)!r}"
                    )
                packages.append(q)
            self.package_paths = packages
        if self.src_dirs is not None:
            src_dirs: list[Path] = []
            for p in self.src_dirs:
                q = base / p
                if not q.is_dir():
                    raise UserInputError(f"src_dir: not a directory: {str(q)!r}")
                src_dirs.append(q)
            self.src_dirs = src_dirs

    def update(self, cfg: Configuration) -> None:
        """
        Update this `Configuration` instance by copying over all non-`None`
        fields from ``cfg``
        """
        for field, value in cfg.model_dump(exclude_none=True).items():
            setattr(self, field, value)

    def get_selected_checks(self) -> set[Check]:
        """
        Return the final set of selected checks according to the ``select`` and
        ``ignore`` options.  This equals the set ``select`` (defaulting to all
        checks if `None`) minus the checks in ``ignore`` (if any).
        """
        if self.select is None:
            selected = set(Check)
        else:
            selected = self.select.copy()
        if self.ignore is not None:
            selected -= self.ignore
        return selected

    def get_package_tree(self) -> Optional[Directory]:
        """
        Return the combined file tree obtained by traversing all of the paths
        in ``package_paths`` and ``src_dirs``.  If both fields are `None`,
        return `None`.

        :raises UserInputError: if any two subtrees share a toplevel name
        """
        if self.package_paths is None and self.src_dirs is None:
            return None
        if self.package_omit is None:
            exclude = TRAVERSAL_EXCLUSIONS
        else:
            exclude = self.package_omit
        tree = Directory()
        for p in self.package_paths or []:
            subtree = Directory.from_local_tree(p, exclude=exclude)
            ### TODO: Move the below logic to Directory?
            for name, entry in subtree.entries.items():
                if name in tree:
                    raise UserInputError(
                        f"`--package {p}` adds {name!r} to file tree, but it is"
                        f" already present from prior --package option"
                    )
                tree.entries[name] = entry
        for p in self.src_dirs or []:
            subtree = Directory.from_local_tree(
                p,
                exclude=exclude,
                include_root=False,
            )
            ### TODO: Move the below logic to Directory?
            for name, entry in subtree.entries.items():
                if name in tree:
                    raise UserInputError(
                        f"`--src-dir {p}` adds {name!r} to file tree, but it is"
                        f" already present from prior --package or --src-dir"
                        f" option"
                    )
                tree.entries[name] = entry
        return tree
