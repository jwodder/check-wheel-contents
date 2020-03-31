from   configparser import ConfigParser
from   pathlib      import Path
from   typing       import Any, List, Mapping, Optional, Set, Tuple
import attr
import toml
from   .checks      import Check, parse_check_prefixes
from   .errors      import UserInputError
from   .filetree    import Directory
from   .util        import comma_split

CONFIG_FILES = [
    'pyproject.toml',
    'tox.ini',
    'setup.cfg',
    'check-wheel-contents.cfg',
    '.check-wheel-contents.cfg',
]

CONFIG_SECTION = 'check-wheel-contents'

TRAVERSAL_EXCLUSIONS = ['.*', 'CVS', 'RCS', '*.pyc', '*.pyo', '*.egg-info']

def convert_toplevel(value: Optional[List[str]]) -> Optional[List[str]]:
    if value is not None:
        value = [tl.rstrip('/') for tl in value]
    return value

@attr.s(auto_attribs=True)
class Configuration:
    select: Optional[Set[Check]] = None
    ignore: Optional[Set[Check]] = None
    toplevel: Optional[List[str]] \
        = attr.ib(default=None, converter=convert_toplevel)
    package_paths: Optional[List[Path]] = None
    src_dirs: Optional[List[Path]] = None
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
        cfgdict: Optional[ConfigDict]
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
        return cls(
            select        = cfgdict.get_check_set("select"),
            ignore        = cfgdict.get_check_set("ignore"),
            toplevel      = cfgdict.get_comma_list("toplevel"),
            package_paths = cfgdict.get_path_list("package"),
            src_dirs      = cfgdict.get_path_list("src_dir"),
            package_omit  = cfgdict.get_comma_list("package_omit"),
        )

    def update(self, cfg: 'Configuration') -> None:
        for field in attr.fields_dict(type(self)).keys():
            newvalue = getattr(cfg, field)
            if newvalue is not None:
                setattr(self, field, newvalue)

    def get_selected_checks(self) -> Set[Check]:
        if self.select is None:
            selected = set(Check)
        else:
            selected = self.select.copy()
        if self.ignore is not None:
            selected -= self.ignore
        return selected

    def get_package_tree(self) -> Optional[Directory]:
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
    configpath: Path
    data: Mapping[str, Any]

    @classmethod
    def find_default(cls) -> Optional['ConfigDict']:
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
        value = self.get_comma_list(key)
        if value is not None:
            try:
                return parse_check_prefixes(value)
            except UserInputError as e:
                raise UserInputError(f'{self.configpath}: {key}: {e}')
        else:
            return None

    def get_path_list(self, key: str) -> Optional[List[Path]]:
        value = self.get_comma_list(key)
        if value is not None:
            base = self.configpath.resolve().parent
            return [base / p for p in value]
        else:
            return None
