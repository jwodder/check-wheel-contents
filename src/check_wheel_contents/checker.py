from   operator  import attrgetter
import re
from   typing    import Any, List, Optional, Set, Tuple
import attr
from   .checks   import Check, FailedCheck
from   .config   import Configuration
from   .contents import WheelContents
from   .filetree import Directory, File
from   .util     import bytes_signature, is_stubs_dir

NO_CONFIG = object()

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
    pkgtree:  Optional[Directory] = None

    @selected.default
    def _selected_default(self) -> Set[Check]:
        return set(Check)

    def configure_options(
        self,
        configpath: Any = NO_CONFIG,
        select: Optional[Set[Check]] = None,
        ignore: Optional[Set[Check]] = None,
        toplevel: Optional[List[str]] = None,
        package: Tuple[str, ...] = (),
        src_dir: Tuple[str, ...] = (),
    ) -> None:
        cfg = Configuration()
        if configpath is not NO_CONFIG:
            if configpath is not None and not isinstance(configpath, str):
                raise TypeError('configpath must be None, str, or NO_CONFIG')
            cfg.update(Configuration.from_config_file(configpath))
        cfg.update(Configuration.from_command_options(
            select   = select,
            ignore   = ignore,
            toplevel = toplevel,
            package  = package,
            src_dir  = src_dir,
        ))
        self.selected = cfg.get_selected_checks()
        self.toplevel = cfg.toplevel
        self.pkgtree = cfg.get_package_tree()

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
        # Not active when --toplevel, --package, or --src-dir given
        if self.toplevel is not None or self.pkgtree is not None:
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
        #W101 = 'Wheel library is missing files in package tree'
        # Checks all regular files in purelib and platlib combined
        # Only active when --package or --src-dir given
        if self.pkgtree is None:
            return []
        missing = {f.path for f in self.pkgtree.all_files()}
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for f in tree.all_files():
                missing.discard(f.libpath)
        if missing:
            return [FailedCheck(Check.W101, sorted(missing))]
        else:
            return []

    def check_W102(self, contents: WheelContents) -> List[FailedCheck]:
        #W102 = 'Wheel library contains files not in package tree'
        # Checks all regular files in purelib and platlib combined
        # Only active when --package or --src-dir given
        if self.pkgtree is None:
            return []
        expected = {f.path for f in self.pkgtree.all_files()}
        extra = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for f in tree.all_files():
                if f.libpath not in expected:
                    extra.append(f.path)
        if extra:
            return [FailedCheck(Check.W102, extra)]
        else:
            return []

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
