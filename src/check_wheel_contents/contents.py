from   collections      import defaultdict
import csv
from   io               import TextIOWrapper
from   keyword          import iskeyword
from   os.path          import basename, splitext
import re
from   typing           import Dict, Iterator, List, Optional, Tuple, Union
from   zipfile          import ZipFile
import attr
from   property_manager import cached_property
from   wheel_filename   import parse_wheel_filename
from   .errors          import WheelValidationError
from   .util            import is_data_dir, is_dist_info_dir, pymodule_basename

ROOT_IS_PURELIB_RGX = re.compile(r'Root-Is-Purelib\s*:\s*(.*?)\s*', flags=re.I)

@attr.s
class WheelContents:
    dist_info_dir   = attr.ib()
    data_dir        = attr.ib()
    root_is_purelib = attr.ib(default=True)
    by_signature    = attr.ib(factory=lambda: defaultdict(list))
    filetree        = attr.ib(factory=lambda: Directory())

    @cached_property
    def purelib_tree(self):
        if self.root_is_purelib:
            return Directory(
                path=None,
                entries={
                    k:v for k,v in self.filetree.entries
                    if k not in (self.dist_info_dir, self.data_dir)
                },
            )
        else:
            try:
                return self.filetree[self.data_dir]['purelib']
            except (KeyError, TypeError):
                return Directory(f'{self.data_dir}/purelib/')

    @cached_property
    def platlib_tree(self):
        if not self.root_is_purelib:
            return Directory(
                path=None,
                entries={
                    k:v for k,v in self.filetree.entries
                    if k not in (self.dist_info_dir, self.data_dir)
                },
            )
        else:
            try:
                return self.filetree[self.data_dir]['platlib']
            except (KeyError, TypeError):
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
        wc.sanity_checks()
        return wc

    def add_record_file(self, fp):
        self.add_record_rows(csv.reader(fp, delimiter=',', quotechar='"'))

    def add_record_rows(self, rows):
        for row in rows:
            if row and row[0].endswith('/'):
                entry = Directory(row[0])
            else:
                entry = File.from_record_row(row)
            self.add_file(entry)

    def add_entry(self, entry: Union['File', 'Directory']):
        self.filetree.add_entry(entry)
        if isinstance(entry, File):
            self.by_signature[entry.signature].append(entry)
        # Invalidate cached properties:
        del self.purelib_tree
        del self.platlib_tree

    def sanity_checks(self) -> None:
        dist_info_dirs = [
            name for name in self.filetree.subdirectories.keys()
                 if is_dist_info_dir(name)
        ]
        if len(dist_info_dirs) > 1:
            raise WheelValidationError(
                'Wheel contains multiple .dist-info directories'
            )
        elif len(dist_info_dirs) == 1 \
                and dist_info_dirs[0] != self.dist_info_dir:
            raise WheelValidationError(
                f"Wheel's .dist-info directory has invalid name:"
                f" {dist_info_dirs[0]!r}"
            )
        data_dirs = [
            name for name in self.filetree.subdirectories.keys()
                 if is_data_dir(name)
        ]
        if len(data_dirs) > 1:
            raise WheelValidationError(
                'Wheel contains multiple .data directories'
            )
        elif len(data_dirs) == 1 and data_dirs[0] != self.data_dir:
            raise WheelValidationError(
                f"Wheel's .data directory has invalid name: {data_dirs[0]!r}"
            )
        ### TODO: Check that .data and .dist-info are directories
        ### TODO: Check that entries in .data (at least purelib and platlib)
        ### are directories
        ### TODO: Check that .data/purelib is not present when Root-Is-Purelib
        ### and .data/platlib is not present when it's not


@attr.s(auto_attribs=True, frozen=True)
class File:
    parts:   Tuple[str]    = attr.ib()
    size:    Optional[int] = attr.ib()
    hashsum: Optional[str] = attr.ib()

    @classmethod
    def from_record_row(cls, row: List[str]):
        try:
            path, hashsum, size = row
            size = int(size) if size else None
        except ValueError:
            raise WheelValidationError(f'Invalid RECORD entry: {row!r}')
        if path.endswith('/'):
            # This is a ValueError, not a WheelValidationError, because it
            # should only happen when the caller messes up.
            raise ValueError(
                f'Invalid file path passed to File.from_record_row(): {path!r}'
            )
        elif path.startswith('/'):
            raise WheelValidationError(f'Absolute path in RECORD: {path!r}')
        elif path == '':
            raise WheelValidationError(f'Empty path in RECORD')
        elif '//' in path:
            raise WheelValidationError(
                f'Non-normalized path in RECORD: {path!r}'
            )
        parts = tuple(path.split('/'))
        if '.' in parts or '..' in parts:
            raise WheelValidationError(
                f'Non-normalized path in RECORD: {path!r}'
            )
        return cls(
            parts   = parts,
            size    = size,
            hashsum = hashsum or None,
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
    def libparts(self):
        """
        The path components of the file relative to the root of the purelib or
        platlib folder, whichever contains it.  If the file is in neither
        purelib nor platlib, return `None`.
        """
        if is_data_dir(self.parts[0]):
            if len(self.parts) > 2 and self.parts[1] in ('purelib', 'platlib'):
                return self.parts[2:]
            else:
                return None
        elif is_dist_info_dir(self.parts[0]):
            return None
        else:
            return self.parts

    @property
    def libpath(self):
        lpp = self.libparts
        return lpp and '/'.join(lpp)

    @property
    def extension(self):
        return splitext(self.parts[-1])[1]

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
            p.isidentifier() and not iskeyword(p) for p in (*pkgs, base)
        )


@attr.s(auto_attribs=True)
class Directory:
    path: Optional[str] = attr.ib(default=None)
    entries: Dict[str, Union[File, 'Directory']] = attr.Factory(dict)

    @path.validator
    def _validate_path(self, attribute, value):
        if value is not None and not value.endswith('/'):
            # This is a ValueError, not a WheelValidationError, because it
            # should only happen when the caller messes up.
            raise ValueError(
                f'Invalid directory path passed as Directory.path: {value!r}'
            )

    @property
    def parts(self) -> Tuple[str]:
        if self.path is None:
            return ()
        else:
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

    def __getitem__(self, value):
        return self.entries[value]

    def add_entry(self, entry: Union[File, 'Directory']):
        if isinstance(entry, Directory) and bool(entry):
            raise ValueError('Cannot add nonempty directory to directory tree')
        myparts = self.parts
        parts = entry.parts
        if not (len(myparts) < len(parts) and myparts == parts[:len(myparts)]):
            raise ValueError(
                f'Path {entry.path!r} is not a descendant of {self.path!r}'
            )
        current: Directory = self
        *dirs, basename = parts[len(myparts):]
        for i,p in enumerate(dirs):
            this_path = '/'.join(dirs[:i+1]) + '/'
            if p in current.entries:
                if isinstance(current.entries[p], Directory):
                    current = current.entries[p]
                else:
                    raise WheelValidationError(
                        f'Conflicting occurrences of path {this_path!r}'
                    )
            else:
                sd = Directory(this_path)
                current.entries[p] = sd
                current = sd
        if basename in current.entries:
            if not (isinstance(entry, Directory)
                    and isinstance(current.entries[basename], Directory)):
                raise WheelValidationError(
                    f'Conflicting occurrences of path {entry.path!r}'
                )
        else:
            current.entries[basename] = entry

    def all_files(self) -> Iterator[File]:
        for e in self.entries.values():
            if isinstance(e, Directory):
                yield from e.all_files()
            else:
                yield e
