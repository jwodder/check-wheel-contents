from   collections  import defaultdict
import csv
from   enum         import Enum
from   io           import TextIOWrapper
from   os.path      import basename, splitext
import re
from   zipfile      import ZipFile
import attr
from   .whlfilename import parse_wheel_filename

# <https://discuss.python.org/t/identifying-parsing-binary-extension-filenames/>
MODULE_EXT_RGX = re.compile(r'(?:\.py|\.[-A-Za-z0-9_]+\.(?:pyd|so))\Z')

ROOT_IS_PURELIB_RGX = re.compile(
    r'\s*Root-Is-Purelib\s*:\s*(.*?)\s*',
    flags=re.I,
)

class FileSection(Enum):
    PURELIB   = 1
    PLATLIB   = 2
    MISC_DATA = 3
    DIST_INFO = 4


@attr.s
class WheelContents:
    dist_info_dir   = attr.ib()
    data_dir        = attr.ib()
    root_is_purelib = attr.ib(default=True)
    #: Set of all toplevel elements in the purelib and platlib sections (i.e.,
    #: all `entry.libparts[0]` values)
    lib_toplevel    = attr.ib(factory=set)
    #: Set of all toplevel directories in the purelib and platlib sections
    #: (i.e., all `entry.libparts[0]` values where `len(entry.libparts) > 1`)
    lib_dirs        = attr.ib(factory=set)
    #: Set of all toplevel directories in the purelib and platlib that contain
    #: Python files at valid module paths (TODO: Should the "at valid module
    #: paths" condition be dropped?)
    lib_pkg_roots   = attr.ib(factory=set)
    files           = attr.ib(factory=list)
    by_signature    = attr.ib(factory=lambda: defaultdict(list))

    @classmethod
    def from_wheel(cls, path):
        whlname = parse_wheel_filename(basename(path))
        dist_info_dir = f'{whlname.project}-{whlname.version}.dist-info'
        data_dir = f'{whlname.project}-{whlname.version}.data'
        wc = cls(dist_info_dir=dist_info_dir, data_dir=data_dir)
        with open(path, 'rb') as fp, ZipFile(fp) as zf:
            for filename in zf.namelist():
                with zf.open(f'{dist_info_dir}/RECORD') as rf:
                    wc.add_record_file(TextIOWrapper(rf, 'utf-8', newline=''))
                with zf.open(f'{dist_info_dir}/WHEEL') as wf:
                    for line in TextIOWrapper(wf, 'utf-8'):
                        m = ROOT_IS_PURELIB_RGX.fullmatch(line)
                        if m:
                            rip = m.group(1)
                            if rip.lower() == 'true':
                                wc.root_is_purelib = True
                            elif rip.lower() == 'false':
                                wc.root_is_purelib = False
                            else:
                                raise ValueError(
                                    f'Invalid Root-Is-Purelib value in WHEEL'
                                    f' file: {rip}'
                                )
                            break
                    else:
                        raise ValueError(
                            'Root-Is-Purelib header not found in WHEEL file'
                        )
        return wc

    def add_record_file(self, fp):
        self.add_record_rows(csv.reader(fp, delimiter=',', quotechar='"'))

    def add_record_rows(self, rows):
        for row in rows:
            entry = FileEntry.from_record_row(self, row)
            self.add_file(entry)

    def add_file(self, entry):
        if entry.in_library():
            self.lib_toplevel.add(entry.libparts[0])
            if len(entry.libparts) > 1:
                self.lib_dirs.add(entry.libparts[0])
                if entry.valid_module_path():
                    self.lib_pkg_roots.add(entry.libparts[0])
        self.files.append(entry)
        self.by_signature[entry.signature].append(entry)

    @property
    def filepaths(self):
        return [f.path for f in self.files]

    @property
    def fileparts(self):
        return [f.parts for f in self.files]

    @property
    def path_set(self):
        return {f.parts for f in self.files}

    def categorize_path(self, path):
        parts = tuple(path.split('/'))
        if parts[0] == self.data_dir:
            if len(parts) > 2 and parts[1] == 'purelib':
                return (FileSection.PURELIB, parts[2:])
            elif len(parts) > 2 and parts[1] == 'platlib':
                return (FileSection.PLATLIB, parts[2:])
            else:
                return (FileSection.DATA, None)
        elif parts[0] == self.dist_info_dir:
            return (FileSection.DIST_INFO, None)
        elif self.root_is_purelib:
            return (FileSection.PURELIB, parts)
        else:
            return (FileSection.PLATLIB, parts)


@attr.s(frozen=True)
class FileEntry:
    parts    = attr.ib()
    libparts = attr.ib()
    size     = attr.ib()
    hashsum  = attr.ib()
    section  = attr.ib()

    @classmethod
    def from_record_row(cls, whlcon, row):
        try:
            path, hashsum, size = row
            size = int(size) if size else None
        except ValueError:
            raise ValueError(f'Invalid RECORD entry: {row!r}')
        parts = tuple(path.split('/'))
        section, libparts = whlcon.categorize_path(path)
        return cls(
            parts    = parts,
            libparts = libparts,
            size     = size,
            hashsum  = hashsum or None,
            section  = section,
        )

    @property
    def path(self):
        return '/'.join(self.parts)

    @property
    def signature(self):
        return (self.size, self.hashsum)

    @property
    def libpath(self):
        lpp = self.libparts
        return lpp and '/'.join(lpp)

    @property
    def extension(self):
        return splitext(self.parts[-1])[1]

    def in_library(self):
        return self.section in (FileSection.PURELIB, FileSection.PLATLIB)

    def is_module(self):
        return MODULE_EXT_RGX.search(self.parts[-1]) is not None

    def valid_module_path(self):
        if self.libparts is None:
            return False
        *pkgs, basename = self.libparts
        m = MODULE_EXT_RGX.search(basename)
        if m is None:
            return False
        base = basename[:m.start()]
        return all(
            p.isidentifier() and not p.iskeyword() for p in (*pkgs, base)
        )
