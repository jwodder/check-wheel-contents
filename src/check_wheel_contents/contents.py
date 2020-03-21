from   collections  import defaultdict
import csv
from   enum         import Enum
from   io           import TextIOWrapper
from   os.path      import basename, splitext
import re
from   zipfile      import ZipFile
import attr
from   .directory   import Directory
from   .util        import pymodule_basename
from   .whlfilename import parse_wheel_filename

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
    files           = attr.ib(factory=list)
    by_signature    = attr.ib(factory=lambda: defaultdict(list))
    purelib_tree    = attr.ib(factory=Directory)
    platlib_tree    = attr.ib(factory=Directory)

    @classmethod
    def from_wheel(cls, path):
        whlname = parse_wheel_filename(basename(path))
        dist_info_dir = f'{whlname.project}-{whlname.version}.dist-info'
        data_dir = f'{whlname.project}-{whlname.version}.data'
        wc = cls(dist_info_dir=dist_info_dir, data_dir=data_dir)
        with open(path, 'rb') as fp, ZipFile(fp) as zf:
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
            with zf.open(f'{dist_info_dir}/RECORD') as rf:
                wc.add_record_file(TextIOWrapper(rf, 'utf-8', newline=''))
        return wc

    def add_record_file(self, fp):
        self.add_record_rows(csv.reader(fp, delimiter=',', quotechar='"'))

    def add_record_rows(self, rows):
        for row in rows:
            entry = FileEntry.from_record_row(self, row)
            self.add_file(entry)

    def add_file(self, entry):
        self.files.append(entry)
        self.by_signature[entry.signature].append(entry)
        if entry.section is FileSection.PURELIB:
            self.purelib_tree.add_at_path(entry, entry.libparts)
        elif entry.section is FileSection.PLATLIB:
            self.platlib_tree.add_at_path(entry, entry.libparts)

    @property
    def purelib_path_prefix(self):
        if self.root_is_purelib:
            return ''
        else:
            return f'{self.data_dir}/purelib/'

    @property
    def platlib_path_prefix(self):
        if not self.root_is_purelib:
            return ''
        else:
            return f'{self.data_dir}/platlib/'

    def categorize_path(self, path):
        parts = tuple(path.split('/'))
        if parts[0] == self.data_dir:
            if len(parts) > 2 and parts[1] == 'purelib':
                return (FileSection.PURELIB, parts[2:])
            elif len(parts) > 2 and parts[1] == 'platlib':
                return (FileSection.PLATLIB, parts[2:])
            else:
                return (FileSection.MISC_DATA, None)
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

    def __str__(self):
        return self.path

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

    def has_module_ext(self):
        return pymodule_basename(self.parts[-1]) is not None

    def valid_module_path(self):
        if self.libparts is None:
            return False
        *pkgs, basename = self.libparts
        base = pymodule_basename(basename)
        if base is None:
            return False
        return all(
            p.isidentifier() and not p.iskeyword() for p in (*pkgs, base)
        )
