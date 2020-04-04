from   configparser import ConfigParser
from   pathlib      import Path
from   typing       import Any, List, Mapping, Optional, Set, Tuple
import attr
import toml
from   .checks      import Check, parse_check_prefixes
from   .errors      import UserInputError
from   .filetree    import Directory
from   .util        import comma_split

#: The filenames that configuration is read from by default, in descending
#: order of preference
CONFIG_FILES = [
    'pyproject.toml',
    'tox.ini',
    'setup.cfg',
    'check-wheel-contents.cfg',
    '.check-wheel-contents.cfg',
]

#: The name of the configuration section from which the configuration is
#: retrieved for most configuration formats
CONFIG_SECTION = 'check-wheel-contents'

#: The default set of exclusion patterns for traversing ``--package`` and
#: ``--src-dir`` directories
TRAVERSAL_EXCLUSIONS = ['.*', 'CVS', 'RCS', '*.pyc', '*.pyo', '*.egg-info']

def convert_toplevel(value: Optional[List[str]]) -> Optional[List[str]]:
    """
    Strip trailing forward slashes from the elements of a list, if defined
    """
    if value is not None:
        value = [tl.rstrip('/') for tl in value]
    return value

@attr.s(auto_attribs=True)
class Configuration:
    """ A container for a `WheelChecker`'s raw configuration values """

    #: The set of selected checks, or `None` if not specified
    select: Optional[Set[Check]] = None
    #: The set of ignored checks, or `None` if not specified
    ignore: Optional[Set[Check]] = None
    #: The list of toplevel names to check for with the W2 checks, or `None` if
    #: not specified
    toplevel: Optional[List[str]] \
        = attr.ib(default=None, converter=convert_toplevel)
    #: The list of paths specified with ``--package``, or `None` if not
    #: specified
    package_paths: Optional[List[Path]] = None
    #: The list of paths specified with ``--src-dir``, or `None` if not
    #: specified
    src_dirs: Optional[List[Path]] = None
    #: The set of exclusion patterns for traversing ``package_paths`` and
    #: ``src_dirs``, or `None` if not specified
    package_omit: Optional[List[str]] = None

    @classmethod
    def from_command_options(
        cls,
        select: Optional[Set[Check]] = None,
        ignore: Optional[Set[Check]] = None,
        toplevel: Optional[List[str]] = None,
        package: Tuple[str, ...] = (),
        src_dir: Tuple[str, ...] = (),
        package_omit: Optional[List[str]] = None,
    ) -> 'Configuration':
        """
        Construct a `Configuration` instance from option values passed in on
        the command line.  Elements of ``package`` and ``src_dir`` are
        converted to `Path`s, and if either tuple is empty (indicating that the
        corresponding option was not given on the command line), it is replaced
        by `None`.  All other values are stored as-is.
        """
        package_paths: Optional[List[Path]]
        if package:
            package_paths = [Path(p) for p in package]
        else:
            package_paths = None
        src_dirs: Optional[List[Path]]
        if src_dir:
            src_dirs = [Path(p) for p in src_dir]
        else:
            src_dirs = None
        return cls(
            select        = select,
            ignore        = ignore,
            toplevel      = toplevel,
            package_paths = package_paths,
            src_dirs      = src_dirs,
            package_omit  = package_omit,
        )

    @classmethod
    def from_config_file(cls, path: Optional[str] = None) -> 'Configuration':
        """
        Construct a `Configuration` instance from the configuration file at the
        given path.  If the path is `None`, read from the default configuration
        file.  If the read configuration file does not contain the appropriate
        section, or if the default configuration file is not found, return a
        `Configuration` instance with all-default values.
        """
        if path is None:
            cfgdict = ConfigDict.find_default()
        else:
            cfgdict = ConfigDict.from_file(Path(path))
        if cfgdict is None:
            return cls()
        else:
            return cls.from_config_dict(cfgdict)

    @classmethod
    def from_config_dict(cls, cfgdict: 'ConfigDict') -> 'Configuration':
        """ Construct a `Configuration` instance from a `ConfigDict` """
        return cls(
            select        = cfgdict.get_check_set("select"),
            ignore        = cfgdict.get_check_set("ignore"),
            toplevel      = cfgdict.get_comma_list("toplevel"),
            package_paths = cfgdict.get_path_list("package"),
            src_dirs      = cfgdict.get_path_list("src_dir", require_dir=True),
            package_omit  = cfgdict.get_comma_list("package_omit"),
        )

    def update(self, cfg: 'Configuration') -> None:
        """
        Update this `Configuration` instance by copying over all non-`None`
        fields from ``cfg``
        """
        for field in attr.fields_dict(type(self)).keys():
            newvalue = getattr(cfg, field)
            if newvalue is not None:
                setattr(self, field, newvalue)

    def get_selected_checks(self) -> Set[Check]:
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
        for p in (self.package_paths or []):
            subtree = Directory.from_local_tree(p, exclude=exclude)
            ### TODO: Move the below logic to Directory?
            for name, entry in subtree.entries.items():
                if name in tree:
                    raise UserInputError(
                        f'`--package {p}` adds {name!r} to file tree, but it is'
                        f' already present from prior --package option'
                    )
                tree.entries[name] = entry
        for p in (self.src_dirs or []):
            subtree = Directory.from_local_tree(
                p,
                exclude      = exclude,
                include_root = False,
            )
            ### TODO: Move the below logic to Directory?
            for name, entry in subtree.entries.items():
                if name in tree:
                    raise UserInputError(
                        f'`--src-dir {p}` adds {name!r} to file tree, but it is'
                        f' already present from prior --package or --src-dir'
                        f' option'
                    )
                tree.entries[name] = entry
        return tree


@attr.s(auto_attribs=True)
class ConfigDict:
    """ The raw data read from a section of a configuration file """

    #: The path to the configuration file
    configpath: Path
    #: The data read from the configuration file
    data: Mapping[str, Any]

    @classmethod
    def find_default(cls) -> Optional['ConfigDict']:
        """
        Find the default configuration file and read the relevant section from
        it.  Returns `None` if no file with the appropriate section is found.
        """
        cwd = Path()
        for d in (cwd, *cwd.resolve().parents):
            found = [d / cf for cf in CONFIG_FILES if (d / cf).exists()]
            if found:
                for p in found:
                    cfgdict = cls.from_file(p)
                    if cfgdict is not None:
                        return cfgdict
                return None
        return None

    @classmethod
    def from_file(cls, path: Path) -> Optional['ConfigDict']:
        """
        Read the relevant section from the given configuration file.  Returns
        `None` if the section does not exist.
        """
        if path.suffix == '.toml':
            data = toml.load(path)
            tool = data.get("tool")
            if not isinstance(tool, dict):
                return None
            cfg = tool.get(CONFIG_SECTION)
            if cfg is None:
                return None
            elif not isinstance(cfg, dict):
                raise UserInputError(
                    f'{path}: tool.{CONFIG_SECTION}: not a table'
                )
            else:
                return cls(path, cfg)
        else:
            data = ConfigParser()
            with path.open(encoding='utf-8') as fp:
                data.read_file(fp)
            if path.name == 'setup.cfg':
                section = f'tool:{CONFIG_SECTION}'
            else:
                section = CONFIG_SECTION
            if data.has_section(section):
                return cls(path, data[section])
            else:
                return None

    def get_comma_list(self, key: str) -> Optional[List[str]]:
        """
        Retrieve the value of the given key from the data, converting it from a
        comma-separated string to a list of strings in the process.  If the
        value is already a list of strings, it is left as-is.  If it is
        anything else, a `UserInputError` is raised.  If the key is not
        present, `None` is returned.
        """
        if key not in self.data:
            return None
        value = self.data[key]
        if isinstance(value, str):
            return comma_split(value)
        elif isinstance(value, list) and all(isinstance(v, str) for v in value):
            return value
        else:
            raise UserInputError(
                f'{self.configpath}: {key}: value must be comma-separated'
                f' string or list of strings'
            )

    def get_check_set(self, key: str) -> Optional[Set[Check]]:
        """
        Retrieve the value of the given key from the data, converting it from
        either a comma-separated string or list of strings of check names &
        check name prefixes to a set of `Check` objects.

        If the value is neither a string nor a list of strings, a
        `UserInputError` is raised.

        If the key is not present, `None` is returned.
        """
        value = self.get_comma_list(key)
        if value is not None:
            try:
                return parse_check_prefixes(value)
            except UserInputError as e:
                raise UserInputError(f'{self.configpath}: {key}: {e}')
        else:
            return None

    def get_path_list(self, key: str, require_dir: bool = False) \
            -> Optional[List[Path]]:
        """
        Retrieve the value of the given key from the data, converting it from
        either a comma-separated string or list of strings to a list of `Path`
        objects resolved relative to the path to the configuration file.

        If the value is neither a string nor a list of strings, a
        `UserInputError` is raised.

        If the key is not present, `None` is returned.

        If a given path does not exist, a `UserInputError` is raised.
        """
        value = self.get_comma_list(key)
        if value is not None:
            base = self.configpath.resolve().parent
            paths = []
            for p in value:
                q = base / p
                if not q.exists():
                    raise UserInputError(
                        f'{self.configpath}: {key}: no such file or directory:'
                        f' {str(q)!r}'
                    )
                elif require_dir and not q.is_dir():
                    raise UserInputError(
                        f'{self.configpath}: {key}: not a directory: {str(q)!r}'
                    )
                paths.append(q)
            return paths
        else:
            return None
