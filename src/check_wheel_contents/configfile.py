from   configparser import ConfigParser
from   pathlib      import Path
from   typing       import Callable, List, Tuple, Union
import toml

def load_ini(path: Path) -> dict:
    cfg = ConfigParser()
    with path.open(encoding='utf-8') as fp:
        cfg.read_file(fp)
    return cfg

DEFAULT_LOADER  = load_ini
DEFAULT_SECTION = 'check-wheel-contents'

CONFIG_FILES: List[Tuple[str, Callable[[Path], dict], str]] = [
    # filename, loader, section name
    # Loaders must raise FileNotFoundError if path does not exist
    ('pyproject.toml',            toml.load,      'tool.check-wheel-contents'),
    ('tox.ini',                   load_ini,       'check-wheel-contents'),
    ('setup.cfg',                 load_ini,       'tool:check-wheel-contents'),
    ('check-wheel-contents.cfg',  DEFAULT_LOADER, DEFAULT_SECTION),
    ('.check-wheel-contents.cfg', DEFAULT_LOADER, DEFAULT_SECTION),
]

def find_config_dict(dirpath: Union[str, Path, None] = None) -> dict:
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
                    return cfg[section]
    return {}

def read_config_dict(path: Path) -> dict:
    cfg = DEFAULT_LOADER(path)
    if DEFAULT_SECTION in cfg:
        return cfg[DEFAULT_SECTION]
    else:
        return {}
