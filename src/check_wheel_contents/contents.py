from   collections      import defaultdict
import csv
from   enum             import Enum
from   io               import TextIOWrapper
from   os.path          import basename, splitext
import re
from   typing           import Dict, Iterator, List, Tuple, Union
from   zipfile          import ZipFile
import attr
from   property_manager import cached_property
from   .util            import InvalidWheelError, pymodule_basename
from   .whlfilename     import parse_wheel_filename

ROOT_IS_PURELIB_RGX = re.compile(
    r'\s*Root-Is-Purelib\s*:\s*(.*?)\s*',
    flags=re.I,
)

class Section(Enum):
    PURELIB   = 1
    PLATLIB   = 2
    MISC_DATA = 3
    DIST_INFO = 4


@attr.s
class WheelContents:
    dist_info_dir   = attr.ib()
    data_dir        = attr.ib()
    root_is_purelib = attr.ib(default=True)
    by_signature    = attr.ib(factory=lambda: defaultdict(list))
    filetree        = attr.ib(factory=lambda: Directory('./'))

    @cached_property
    def purelib_tree(self):
        if self.root_is_purelib:
            return Directory(
                path='./',
                entries={
                    k:v for k,v in self.filetree.entries
                    if k not in (self.dist_info_dir, self.data_dir)
                },
            )
        else:
            try:
                return self.filetree.entries[self.data_dir].entries['purelib']
            except (AttributeError, KeyError):
                return Directory(f'{self.data_dir}/purelib/')

    @cached_property
    def platlib_tree(self):
        if not self.root_is_purelib:
            return Directory(
                path='./',
                entries={
                    k:v for k,v in self.filetree.entries
                    if k not in (self.dist_info_dir, self.data_dir)
                },
            )
        else:
            try:
                return self.filetree.entries[self.data_dir].entries['platlib']
            except (AttributeError, KeyError):
                return Directory(f'{self.data_dir}/platlib/')

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
            if row and row[0].endswith('/'):
                entry = Directory(row[0])
            else:
                entry = File.from_record_row(self, row)
            self.add_file(entry)

    def add_entry(self, entry: Union['File', 'Directory']):
        self.tree.add_entry(entry)
        if isinstance(entry, File):
            self.by_signature[entry.signature].append(entry)
        # Invalidate cached properties:
        del self.purelib_tree
        del self.platlib_tree

    def categorize_path(self, path):
        parts = tuple(path.split('/'))
        if parts[0] == self.data_dir:
            if len(parts) > 2 and parts[1] == 'purelib':
                return (Section.PURELIB, parts[2:])
            elif len(parts) > 2 and parts[1] == 'platlib':
                return (Section.PLATLIB, parts[2:])
            else:
                return (Section.MISC_DATA, None)
        elif parts[0] == self.dist_info_dir:
            return (Section.DIST_INFO, None)
        elif self.root_is_purelib:
            return (Section.PURELIB, parts)
        else:
            return (Section.PLATLIB, parts)


@attr.s(frozen=True)
class File:
    parts    = attr.ib()
    libparts = attr.ib()   ### Remove?
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

    #@property
    #def libpath(self):
    #    lpp = self.libparts
    #    return lpp and '/'.join(lpp)

    @property
    def extension(self):
        return splitext(self.parts[-1])[1]

    #def in_library(self):
    #    return self.section in (Section.PURELIB, Section.PLATLIB)

    def has_module_ext(self):
        return pymodule_basename(self.parts[-1]) is not None

    def is_valid_module_path(self):
        if self.libparts is None:
            return False
        *pkgs, basename = self.libparts
        base = pymodule_basename(basename)
        if base is None:
            return False
        return all(
            p.isidentifier() and not p.iskeyword() for p in (*pkgs, base)
        )


@attr.s(auto_attribs=True)
class Directory:
    path: str = attr.ib()
    entries: Dict[str, Union[File, 'Directory']] = attr.Factory(dict)

    @path.validator
    def _validate_path(self, attribute, value):
        if not value.endswith('/'):
            raise ValueError(
                f'Invalid directory path passed as Directory.path: {value!r}'
            )

    @property
    def parts(self) -> Tuple[str]:
        return tuple(self.path.rstrip('/').split('/'))

    @property
    def subdirectories(self) -> Dict[str, 'Directory']:
        ### TODO: Cache this?
        return {k:v for k,v in self.entries.items() if isinstance(v, Directory)}

    @property
    def files(self) -> Dict[str, File]:
        ### TODO: Cache this?
        return {k:v for k,v in self.entries.items() if isinstance(v, File)}

    def __bool__(self):
        return bool(self.entries)

    def add_entry(self, entry: Union[File, 'Directory']):
        current: Directory = self
        *dirs, basename = entry.parts
        for i,p in enumerate(dirs):
            this_path = '/'.join(dirs[:i+1]) + '/'
            if p in current.entries:
                if isinstance(current.entries[p], Directory):
                    current = current.entries[p]
                else:
                    raise InvalidWheelError(
                        f'Conflicting occurrences of path {this_path!r}'
                    )
            else:
                current = current.entries[p] = Directory(this_path)
        if basename in current.entries:
            raise InvalidWheelError(
                f'Conflicting occurrences of path {entry.path!r}'
            )
        current.entries[basename] = entry

    def all_files(self) -> Iterator[File]:
        for e in self.entries.values():
            if isinstance(e, Directory):
                yield from e.all_files()
            else:
                yield e
