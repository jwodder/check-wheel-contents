from operator import attrgetter
from .checks  import Check, FailedCheck
from .util    import bytes_signature, get_ext

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

@attr.s
class WheelChecker:
    selected = attr.ib()

    @selected.default
    def _selected_default(self):
        return set(Check)

    def apply_command_options(self, **kwargs):
        ???

    def apply_config_dict(self, cfg):
        ???

    def check_contents(self, contents):
        failures = []
        for c in sorted(self.selected, key=attrgetter('name')):
            method = getattr(self, 'check_' + c.name)
            failures.extend(method(contents))
        return failures

    def check_W001(self, contents):
        # 'Wheel contains .pyc/.pyo files'
        badfiles = []
        for f in contents.files:
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
        # Ignore *.pth files (TODO: and py.typed and *.pyi files?)
        badtops = []
        for t in sorted(contents.lib_toplevel):
            if IGNORED_TOPLEVEL_RGX.search(t):
                continue
            # If `t` is neither a directory nor a .py file, fail:
            ### TODO: Allow all module extensions, not just `.py`
            if get_ext(t) != '.py' and t not in contents.lib_dirs:
                badtops.append(t)
        if badtops:
            return [FailedCheck(Check.W003, badtops)]
        else:
            return []

    def check_W004(self, contents):
        # 'Module is not located at importable path'
        # Only checks things under purelib and platlib
        badfiles = []
        for f in contents.files:
            if f.in_library() and f.is_module() and not f.valid_module_path():
                badfiles.append(f)
        if badfiles:
            return [FailedCheck(Check.W004, badfiles)]
        else:
            return []

    def check_W005(self, contents):
    #W005 = 'Wheel contains common toplevel directory in library'
    # Checks for: src, test, tests, doc, docs, example, examples
    # Only checks purelib and platlib
    # TODO: Add a configuration option for explicitly removing (or adding?)
    # values from consideration

    def check_W006(self, contents):
    #W006 = '__init__.py at top level of library'
    # Only checks purelib and platlib

    def check_W007(self, contents):
    #W007 = 'Wheel library is empty'
    # Only errors if both purelib and platlib are empty

    def check_W008(self, contents):
    #W008 = 'Wheel contains multiple toplevel files'
    # Ignores the same things as W003 as well as modules starting with an
    # underscore
    # Not active when certain options given on command line

    def check_W009(self, contents):
    #W009 = 'Toplevel library directory contains no .py files'
    # Only checks purelib and platlib
    # Does not fail on directories that only contain typing files (iff root dir
    # ends with -stubs?)

    def check_W101(self, contents):
    #W101 = 'Wheel contains files not in source tree'
    # Only active when certain option given on command line

    def check_W102(self, contents):
    #W102 = 'Wheel is missing files in source tree'
    # Only active when certain option given on command line

    def check_W201(self, contents):
    #W201 = 'Wheel is missing specifies toplevel entry'
    # Only active when certain option given on command line

    def check_W202(self, contents):
    #W202 = 'Wheel has undeclared toplevel entry'
    # Only active when certain option given on command line
