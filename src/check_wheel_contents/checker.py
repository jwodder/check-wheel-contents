from   operator    import attrgetter
import re
import attr
from   .checks     import Check, FailedCheck, parse_checks_string
from   .configfile import find_config_dict, read_config_dict
from   .contents   import File
from   .util       import UserInputError, bytes_signature

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

COMMON_DIRS = 'doc docs example exmaples src test tests'.split()

@attr.s
class WheelChecker:
    selected = attr.ib()
    options  = attr.ib(factory=dict)

    @selected.default
    def _selected_default(self):
        return set(Check)

    def read_config_file(self, configpath=None):
        if configpath is None:
            cfg = find_config_dict()
        else:
            cfg = read_config_dict(configpath)
        self.load_config_dict(cfg)

    def load_config_dict(self, cfg: dict) -> None:
        if "select" in cfg:
            if not isinstance(cfg["select"], str):
                raise UserInputError('"select" config key must be a string')
            self.options["select"] = parse_checks_string(cfg["select"])
        if "ignore" in cfg:
            if not isinstance(cfg["ignore"], str):
                raise UserInputError('"ignore" config key must be a string')
            self.options["ignore"] = parse_checks_string(cfg["ignore"])

    def load_command_options(self, select=None, ignore=None):
        if select is not None:
            self.options["select"] = select
        if ignore is not None:
            self.options["ignore"] = ignore

    def finalize_options(self):
        select = self.options.pop("select", None)
        if select is not None:
            self.selected = select.copy()
        ignore = self.options.pop("ignore", None)
        if ignore is not None:
            self.selected -= ignore

    def check_contents(self, contents):
        failures = []
        for c in sorted(self.selected, key=attrgetter('name')):
            method = getattr(self, 'check_' + c.name)
            failures.extend(method(contents))
        return failures

    def check_W001(self, contents):
        # 'Wheel contains .pyc/.pyo files'
        badfiles = []
        for f in contents.tree.all_files():
            if f.extension in BYTECODE_SUFFIXES:
                badfiles.append(f.path)
        if badfiles:
            return [FailedCheck(Check.W001, badfiles)]
        else:
            return []

    def check_W002(self, contents):
        # 'Wheel contains duplicate files'
        # Ignore files whose signatures are in ALLOWED_DUPLICATES
        ### TODO: Support reading sets of allowed duplicates from config
        dups = []
        for sig, files in contents.by_signature.items():
            if len(files) > 1 and sig not in ALLOWED_DUPLICATES:
                dups.append(FailedCheck(Check.W002, [f.path for f in files]))
        return dups

    def check_W003(self, contents):
        # 'Wheel contains non-module at library toplevel'
        # Only checks purelib and platlib sections
        # Ignores *.pth files and directories (TODO: and py.typed and *.pyi
        # files?)
        badtops = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for name, entry in sorted(tree.files.items()):
                if IGNORED_TOPLEVEL_RGX.search(name) is None \
                        and not entry.has_module_ext():
                    badtops.append(entry.path)
        if badtops:
            return [FailedCheck(Check.W003, badtops)]
        else:
            return []

    def check_W004(self, contents):
        # 'Module is not located at importable path'
        # Only checks things under purelib and platlib
        badfiles = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for f in tree.all_files():
                if f.has_module_ext() and not f.is_valid_module_path():
                    badfiles.append(f.path)
        if badfiles:
            return [FailedCheck(Check.W004, badfiles)]
        else:
            return []

    def check_W005(self, contents):
        #W005 = 'Wheel contains common toplevel directory in library'
        # Checks for COMMON_DIRS
        # Only checks purelib and platlib
        # TODO: Add a configuration option for explicitly removing (or adding?)
        # values from consideration
        baddirs = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for common in COMMON_DIRS:
                try:
                    d = tree.subdirectories[common]
                except KeyError:
                    pass
                else:
                    baddirs.append(d.path)
        if baddirs:
            return [FailedCheck(Check.W005, baddirs)]
        else:
            return []

    def check_W006(self, contents):
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

    def check_W007(self, contents):
        #W007 = 'Wheel library is empty'
        # Only errors if both purelib and platlib are empty
        # TODO: Disable if there are things in *.data/scripts/ ?
        # TODO: Change to "No files outside .dist-info directory"?
        if not contents.purelib_tree and not contents.platlib_tree:
            return [FailedCheck(Check.W007)]
        else:
            return []

    def check_W008(self, contents):
        #W008 = 'Wheel contains multiple toplevel library entries'
        # Ignores the same files as W003 as well as files & directories
        # starting with an underscore
        # Checks the combination of purelib and platlib
        # TODO: Not active when certain options given on command line
        toplevels = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for name, entry in tree.entries.items():
                if not name.startswith('_') and not (
                    isinstance(entry,File) and IGNORED_TOPLEVEL_RGX.search(name)
                ):
                    toplevels.append(entry.path)
        if len(toplevels) > 1:
            return [FailedCheck(Check.W008, toplevels)]
        else:
            return []

    def check_W009(self, contents):
        #W009 = 'Toplevel library directory contains no modules'
        # Only checks purelib and platlib
        # TODO: Do not fail on directories that only contain typing files (iff
        # root dir ends with -stubs?)
        baddirs = []
        for tree in (contents.purelib_tree, contents.platlib_tree):
            for subdir in tree.subdirectories.values():
                if not any(f.has_module_ext() for f in subdir.all_files()):
                    baddirs.append(subdir.path)
        if baddirs:
            return [FailedCheck(Check.W009, baddirs)]
        else:
            return []

    def check_W101(self, contents):
        #W101 = 'Wheel library contains files not in source tree'
        # Only active when certain option given on command line
        raise NotImplementedError

    def check_W102(self, contents):
        #W102 = 'Wheel library is missing files in source tree'
        # Only active when certain option given on command line
        raise NotImplementedError

    def check_W201(self, contents):
        #W201 = 'Wheel library is missing specified toplevel entry'
        # Only active when certain option given on command line
        raise NotImplementedError

    def check_W202(self, contents):
        #W202 = 'Wheel library has undeclared toplevel entry'
        # Only active when certain option given on command line
        raise NotImplementedError
