from   operator    import attrgetter
import re
from   typing      import Any, Dict, List, Mapping, Optional, Set
import attr
from   .checks     import Check, FailedCheck, parse_checks_string
from   .configfile import find_config_dict, read_config_dict
from   .contents   import WheelContents
from   .errors     import UserInputError
from   .filetree   import File
from   .util       import bytes_signature, comma_split, is_stubs_dir

BYTECODE_SUFFIXES = ('.pyc', '.pyo')

ALLOWED_DUPLICATES = {
    (None, None),
    bytes_signature(b''),
    bytes_signature(b'\n'),
    bytes_signature(b'\r\n'),
    bytes_signature(b'# -*- coding: utf-8 -*-'),
    bytes_signature(b'# -*- coding: utf-8 -*-\n'),
    bytes_signature(b'# -*- coding: utf-8 -*-\n\r'),
}

IGNORED_TOPLEVEL_RGX = re.compile(r'.\.pth\Z')

COMMON_NAMES = '''
    .eggs .nox .tox .venv
    build data dist doc docs example examples src test tests venv
'''.split()

@attr.s(auto_attribs=True)
class WheelChecker:
    selected: Set[Check] = attr.ib()
    toplevel: Optional[List[str]] = None
    options: Dict[str, Any] = attr.ib(factory=dict)

    @selected.default
    def _selected_default(self) -> Set[Check]:
        return set(Check)

    def configure_options(
        self,
        configpath: Optional[str] = None,
        select: Optional[Set[Check]] = None,
        ignore: Optional[Set[Check]] = None,
        toplevel: Optional[List[str]] = None,
    ) -> None:
        self.read_config_file(configpath)
        if select is not None:
            self.options["select"] = select
        if ignore is not None:
            self.options["ignore"] = ignore
        if toplevel is not None:
            self.options["toplevel"] = toplevel
        self.finalize_options()

    def read_config_file(self, configpath: Optional[str] = None) -> None:
        if configpath is None:
            cfg = find_config_dict()
        else:
            cfg = read_config_dict(configpath)
        self.load_config_dict(cfg)

    def load_config_dict(self, cfg: Mapping[str, Any]) -> None:
        if "select" in cfg:
            if not isinstance(cfg["select"], str):
                raise UserInputError('"select" config key must be a string')
            self.options["select"] = parse_checks_string(cfg["select"])
        if "ignore" in cfg:
            if not isinstance(cfg["ignore"], str):
                raise UserInputError('"ignore" config key must be a string')
            self.options["ignore"] = parse_checks_string(cfg["ignore"])
        if "toplevel" in cfg:
            if not isinstance(cfg["toplevel"], str):
                raise UserInputError('"toplevel" config key must be a string')
            self.options["toplevel"] = comma_split(cfg["toplevel"])

    def finalize_options(self) -> None:
        select = self.options.pop("select", None)
        if select is not None:
            self.selected = select.copy()
        ignore = self.options.pop("ignore", None)
        if ignore is not None:
            self.selected -= ignore
        toplevel = self.options.pop("toplevel", None)
        if toplevel is not None:
            self.toplevel = [tl.rstrip('/') for tl in toplevel]

    def check_contents(self, contents: WheelContents) -> List[FailedCheck]:
        failures = []
        for c in sorted(self.selected, key=attrgetter('name')):
            method = getattr(self, 'check_' + c.name)
            failures.extend(method(contents))
        return failures

    def check_W001(self, contents: WheelContents) -> List[FailedCheck]:
        # 'Wheel contains .pyc/.pyo files'
        badfiles = []
        for f in contents.filetree.all_files():
            if f.extension in BYTECODE_SUFFIXES:
                badfiles.append(f.path)
        if badfiles:
            return [FailedCheck(Check.W001, badfiles)]
        else:
            return []

    def check_W002(self, contents: WheelContents) -> List[FailedCheck]:
        # 'Wheel contains duplicate files'
        # Ignore files whose signatures are in ALLOWED_DUPLICATES
        ### TODO: Support reading sets of allowed duplicates from config
        dups = []
        for sig, files in contents.by_signature.items():
            if len(files) > 1 and sig not in ALLOWED_DUPLICATES:
                dups.append(FailedCheck(Check.W002, [f.path for f in files]))
        return dups

    def check_W003(self, contents: WheelContents) -> List[FailedCheck]:
        # 'Wheel contains non-module at library toplevel'
        # Only checks purelib and platlib sections
        # Ignores *.pth files and directories
        # Note that py.typed and *.pyi file belong inside packages, not at top
        # level.  See the last paragraph of "Packaging Type Information" in PEP
        # 561.
        badtops = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for name, entry in tree.files.items():
                if IGNORED_TOPLEVEL_RGX.search(name) is None \
                        and not entry.has_module_ext():
                    badtops.append(entry.path)
        if badtops:
            return [FailedCheck(Check.W003, badtops)]
        else:
            return []

    def check_W004(self, contents: WheelContents) -> List[FailedCheck]:
        # 'Module is not located at importable path'
        # Only checks things under purelib and platlib
        # TODO: Ignore __init__.py files underneath *-stubs?  Or are those not
        # supposed to be there?
        badfiles = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for f in tree.all_files():
                if f.has_module_ext() and not f.is_valid_module_path():
                    badfiles.append(f.path)
        if badfiles:
            return [FailedCheck(Check.W004, badfiles)]
        else:
            return []

    def check_W005(self, contents: WheelContents) -> List[FailedCheck]:
        #W005 = 'Wheel contains common toplevel name in library'
        # Checks for COMMON_NAMES
        # Only checks purelib and platlib
        # TODO: Add a configuration option for explicitly removing (or adding?)
        # values from consideration?
        badpaths = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for common in COMMON_NAMES:
                try:
                    entry = tree[common]
                except KeyError:
                    pass
                else:
                    badpaths.append(entry.path)
        if badpaths:
            return [FailedCheck(Check.W005, badpaths)]
        else:
            return []

    def check_W006(self, contents: WheelContents) -> List[FailedCheck]:
        #W006 = '__init__.py at top level of library'
        # Only checks purelib and platlib
        badfiles = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            try:
                init_entry = tree.files["__init__.py"]
            except KeyError:
                pass
            else:
                badfiles.append(init_entry.path)
        if badfiles:
            return [FailedCheck(Check.W006, badfiles)]
        else:
            return []

    def check_W007(self, contents: WheelContents) -> List[FailedCheck]:
        #W007 = 'Wheel library is empty'
        # Only errors if both purelib and platlib are empty
        if not contents.purelib_tree and not contents.platlib_tree:
            return [FailedCheck(Check.W007)]
        else:
            return []

    def check_W008(self, contents: WheelContents) -> List[FailedCheck]:
        #W008 = 'Wheel is empty'
        # Errors if there are no files outside .dist-info
        for name in contents.filetree.entries.keys():
            if name != contents.dist_info_dir:
                return []
        return [FailedCheck(Check.W008)]

    def check_W009(self, contents: WheelContents) -> List[FailedCheck]:
        #W009 = 'Wheel contains multiple toplevel library entries'
        # Ignores the same files as W003 as well as files & directories
        # starting with an underscore
        # Checks the combination of purelib and platlib
        # Not active when --toplevel given
        if self.toplevel is not None:
            return []
        toplevels = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for name, entry in tree.entries.items():
                if not name.startswith('_') and not (
                    isinstance(entry,File) and IGNORED_TOPLEVEL_RGX.search(name)
                ):
                    toplevels.append(entry.path)
        if len(toplevels) > 1:
            return [FailedCheck(Check.W009, toplevels)]
        else:
            return []

    def check_W010(self, contents: WheelContents) -> List[FailedCheck]:
        #W010 = 'Toplevel library directory contains no Python modules'
        # Only checks purelib and platlib
        # *-stubs directories are ignored
        baddirs = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for name, subdir in tree.subdirectories.items():
                if not is_stubs_dir(name) and not any(
                    f.has_module_ext() for f in subdir.all_files()
                ):
                    baddirs.append(subdir.path)
        if baddirs:
            return [FailedCheck(Check.W010, baddirs)]
        else:
            return []

    def check_W101(self, contents: WheelContents) -> List[FailedCheck]:
        #W101 = 'Wheel library is missing files in source tree'
        # Only active when certain option given on command line
        raise NotImplementedError

    def check_W102(self, contents: WheelContents) -> List[FailedCheck]:
        #W102 = 'Wheel library contains files not in source tree'
        # Only active when certain option given on command line
        raise NotImplementedError

    def check_W201(self, contents: WheelContents) -> List[FailedCheck]:
        #W201 = 'Wheel library is missing specified toplevel entry'
        # Only active when --toplevel given
        if self.toplevel is None:
            return []
        missing = []
        for name in self.toplevel:
            if name not in contents.purelib_tree \
                    and name not in contents.platlib_tree:
                missing.append(name)
        if missing:
            return [FailedCheck(Check.W201, missing)]
        else:
            return []

    def check_W202(self, contents: WheelContents) -> List[FailedCheck]:
        #W202 = 'Wheel library has undeclared toplevel entry'
        # Ignores *.pth files
        # Only active when --toplevel given
        if self.toplevel is None:
            return []
        expected = set(self.toplevel)
        extra = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for name, entry in tree.entries.items():
                if name not in expected and not (
                    isinstance(entry,File) and IGNORED_TOPLEVEL_RGX.search(name)
                ):
                    extra.append(entry.path)
        if extra:
            return [FailedCheck(Check.W202, extra)]
        else:
            return []
