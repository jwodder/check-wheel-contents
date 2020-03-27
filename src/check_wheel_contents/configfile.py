from   configparser import ConfigParser
import os
from   pathlib      import Path
from   typing       import Any, Callable, List, Mapping, Tuple, Union
import toml
from   .errors      import UserInputError

def load_ini(path: Path) -> Mapping[str, Any]:
    cfg = ConfigParser()
    with path.open(encoding='utf-8') as fp:
        cfg.read_file(fp)
    return cfg

DEFAULT_LOADER  = load_ini
DEFAULT_SECTION = 'check-wheel-contents'

CONFIG_FILES: List[Tuple[str, Callable[[Path], Mapping[str, Any]], str]] = [
    # filename, loader, section name
    # Loaders must raise FileNotFoundError if path does not exist
    ('pyproject.toml',            toml.load,      'tool.check-wheel-contents'),
    ('tox.ini',                   load_ini,       'check-wheel-contents'),
    ('setup.cfg',                 load_ini,       'tool:check-wheel-contents'),
    ('check-wheel-contents.cfg',  DEFAULT_LOADER, DEFAULT_SECTION),
    ('.check-wheel-contents.cfg', DEFAULT_LOADER, DEFAULT_SECTION),
]

def find_config_dict(dirpath: Union[str,Path,None] = None) -> Mapping[str, Any]:
    if dirpath is None:
        dirpath = Path()
    else:
        dirpath = Path(dirpath)
    for d in (dirpath, *dirpath.resolve().parents):
        for filename, loader, section in CONFIG_FILES:
            try:
                cfg = loader(d / filename)
            except FileNotFoundError:
                pass
            else:
                if section in cfg:
                    subcfg = cfg[section]
                    if not isinstance(subcfg, dict):
                        raise UserInputError(
                            f'{d/filename}: {section} is not a dict'
                        )
                    return subcfg
    return {}

def read_config_dict(filepath: Union[str, os.PathLike]) -> dict:
    path = Path(filepath)
    loader: Callable[[Path], Mapping[str, Any]]
    if path.suffix == '.toml':
        loader = toml.load
        section = 'tool.check-wheel-contents'
    else:
        loader = DEFAULT_LOADER
        section = DEFAULT_SECTION
    cfg = loader(path)
    if section in cfg:
        subcfg = cfg[section]
        if not isinstance(subcfg, dict):
            raise UserInputError(f'{path}: {section} is not a dict')
        return subcfg
    else:
        return {}
