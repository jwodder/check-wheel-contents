from   keyword          import iskeyword
from   os.path          import splitext
from   typing           import Dict, Iterator, List, Optional, Tuple, Union
import attr
from   .errors          import WheelValidationError
from   .util            import is_data_dir, is_dist_info_dir, \
                                    pymodule_basename, validate_path

@attr.s(auto_attribs=True, frozen=True)
class File:
    parts:   Tuple[str, ...]    = attr.ib()
    size:    Optional[int] = attr.ib()
    hashsum: Optional[str] = attr.ib()

    @classmethod
    def from_record_row(cls, row: List[str]) -> 'File':
        try:
            path, hashsum, size_str = row
            size = int(size_str) if size_str else None
        except ValueError:
            raise WheelValidationError(f'Invalid RECORD entry: {row!r}')
        if path.endswith('/'):
            # This is a ValueError, not a WheelValidationError, because it
            # should only happen when the caller messes up.
            raise ValueError(
                f'Invalid file path passed to File.from_record_row(): {path!r}'
            )
        validate_path(path)
        return cls(
            parts   = tuple(path.split('/')),
            size    = size,
            hashsum = hashsum or None,
        )

    def __str__(self) -> str:
        return self.path

    @property
    def path(self) -> str:
        return '/'.join(self.parts)

    @property
    def signature(self) -> Tuple[Optional[int], Optional[str]]:
        return (self.size, self.hashsum)

    @property
    def libparts(self) -> Optional[Tuple[str, ...]]:
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
    def extension(self) -> str:
        return splitext(self.parts[-1])[1]

    def has_module_ext(self) -> bool:
        return pymodule_basename(self.parts[-1]) is not None

    def is_valid_module_path(self) -> bool:
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
    def _validate_path(self, attribute: attr.Attribute, value: Optional[str]) -> None:
        if value is not None:
            if not value.endswith('/'):
                # This is a ValueError, not a WheelValidationError, because it
                # should only happen when the caller messes up.
                raise ValueError(
                    f'Invalid directory path passed as Directory.path: {value!r}'
                )
            validate_path(value)

    @property
    def parts(self) -> Tuple[str, ...]:
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

    def __bool__(self) -> bool:
        return bool(self.entries)

    def __getitem__(self, value: str) -> Union[File, 'Directory']:
        return self.entries[value]

    def __contains__(self, value: str) -> bool:
        return value in self.entries

    def add_entry(self, entry: Union[File, 'Directory']) -> None:
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
            this_path = '/'.join(dirs[:i+1])
            if p in current.entries:
                q = current.entries[p]
                if isinstance(q, Directory):
                    current = q
                else:
                    raise WheelValidationError(
                        f'Conflicting occurrences of path {this_path!r}'
                    )
            else:
                sd = Directory(this_path + '/')
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
