import errno
from   keyword import iskeyword
import os
from   os.path import splitext
from   pathlib import Path
from   typing  import Dict, Iterator, List, Optional, Tuple, Union
import attr
from   .errors import WheelValidationError
from   .util   import is_data_dir, is_dist_info_dir, pymodule_basename, \
                        validate_path

@attr.s(auto_attribs=True, frozen=True)
class File:
    """ Representation of a file in a file tree"""

    #: The components of the file's path within the file tree
    parts:   Tuple[str, ...]
    #: The file's size, or `None` if unknown/irrelevant
    size:    Optional[int]
    #: A hash of the file's contents in the same ``{alg}={digest}`` form as
    #: used by :file:`RECORD` files in wheels, or `None` if unknown/irrelevant
    hashsum: Optional[str]

    @classmethod
    def from_record_row(cls, row: List[str]) -> 'File':
        """
        Construct a `File` object from a row of fields in a wheel's
        :file:`RECORD` file
        """
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
        """
        The file's path within the file tree, relative to the root, using ``/``
        as a component separator
        """
        return '/'.join(self.parts)

    @property
    def signature(self) -> Tuple[Optional[int], Optional[str]]:
        """ A tuple of the file's ``size`` and ``hashsum`` fields """
        return (self.size, self.hashsum)

    @property
    def libparts(self) -> Optional[Tuple[str, ...]]:
        """
        The path components of the file relative to the root of the purelib or
        platlib folder, whichever contains it.  If the file is in neither the
        purelib nor platlib section, return `None`.
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
    def libpath(self) -> Optional[str]:
        """
        The file's path relative to the root of the purelib or platlib folder,
        whichever contains it.  If the file is in neither the purelib nor
        platlib section, return `None`.
        """
        lpp = self.libparts
        if lpp:
            return '/'.join(lpp)
        else:
            return None

    @property
    def extension(self) -> str:
        """ The file's filename extension """
        return splitext(self.parts[-1])[1]

    def has_module_ext(self) -> bool:
        """
        Returns `True` iff the file has a file extension indicating it is a
        Python module (either source or binary extension)
        """
        return pymodule_basename(self.parts[-1]) is not None

    def is_valid_module_path(self) -> bool:
        """
        Returns `True` iff the file's ``libpath`` is non-`None` and a valid
        path to a Python module, i.e., iff the file extension indicates it is a
        Python module and all path components (once the file extension is
        removed) are valid (non-keyword) Python identifiers
        """
        if self.libparts is None:
            return False
        *pkgs, basename = self.libparts
        base = pymodule_basename(basename)
        if base is None:
            return False
        return all(p.isidentifier() and not iskeyword(p) for p in (*pkgs, base))


@attr.s(auto_attribs=True)
class Directory:
    """ Representation of a file in a file tree"""

    #: The directory's path within the file tree, relative to the root, using
    #: ``/`` as a component separator, and terminated with ``/``; or `None` if
    #: this directory is the root of the tree
    path: Optional[str] = attr.ib(default=None)
    #: Entries in the directory, as a mapping from basenames to entries
    entries: Dict[str, Union[File, 'Directory']] = attr.Factory(dict)

    @path.validator
    def _validate_path(self, attribute: attr.Attribute, value: Optional[str]) \
            -> None:
        if value is not None:
            if not value.endswith('/'):
                # This is a ValueError, not a WheelValidationError, because it
                # should only happen when the caller messes up.
                raise ValueError(f'Invalid Directory.path value: {value!r}')
            validate_path(value)

    @property
    def parts(self) -> Tuple[str, ...]:
        """
        The components of the directory's path within the file tree.  For the
        root of a file tree, this is the empty tuple.
        """
        if self.path is None:
            return ()
        else:
            return tuple(self.path.rstrip('/').split('/'))

    @property
    def subdirectories(self) -> Dict[str, 'Directory']:
        """
        The directories in the directory, as a mapping from basenames to
        `Directory` objects
        """
        ### TODO: Cache this?
        return {k:v for k,v in self.entries.items() if isinstance(v, Directory)}

    @property
    def files(self) -> Dict[str, File]:
        """
        The files in the directory, as a mapping from basenames to `File`
        objects
        """
        ### TODO: Cache this?
        return {k:v for k,v in self.entries.items() if isinstance(v, File)}

    def __bool__(self) -> bool:
        """ A `Directory` is true iff it is nonempty. """
        return bool(self.entries)

    def __getitem__(self, value: str) -> Union[File, 'Directory']:
        """ Retrieve an entry from the directory by basename """
        return self.entries[value]

    def __contains__(self, value: str) -> bool:
        """
        Returns `True` if ``value`` is the basename of an entry in the
        directory
        """
        return value in self.entries

    def add_entry(self, entry: Union[File, 'Directory']) -> None:
        """
        Insert a `File` or empty `Directory` into the file tree rooted at the
        directory, creating intermediate subdirectories as needed.  If ``path``
        is non-`None`, ``entry.path`` must be a descendant of it.
        """
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
        """
        Return a generator of all `File` objects in the file tree rooted at the
        directory
        """
        for e in self.entries.values():
            if isinstance(e, Directory):
                yield from e.all_files()
            else:
                yield e

    @classmethod
    def from_local_tree(
        cls,
        root: Path,
        exclude: Optional[List[str]] = None,
        include_root: bool = True,
    ) -> 'Directory':
        """
        Construct a file tree mirroring the structure on the local disk at
        ``root``.

        The return value is a `Directory` whose ``path`` is `None`.

        If ``root`` is a regular file, the returned `Directory` will contain a
        `File` with the same name as ``root``, regardless of the value of
        ``include_root``.

        If ``root`` is a directory and ``include_root`` is `True`, the
        returned `Directory` will contain a `Directory` with the same name as
        ``root`` that in turn contains `File` and `Directory` entries with the
        same names as ``root``'s entries, etc.

        If ``root`` is a directory and ``include_root`` is `False`, the
        returned `Directory` will contain `File` and `Directory` entries with
        the same names as ``root``'s entries, etc.

        File & directories within root (but not ``root`` itself) that match any
        of the patterns in ``exclude`` will be omitted from the resulting tree.

        :raises FileNotFoundError: if ``root`` does not exist
        """
        if exclude is None:
            exclude_list = []
        else:
            exclude_list = exclude
        dir_root = cls()
        if not root.exists():
            # <https://stackoverflow.com/a/36077407>
            raise FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                str(root),
            )
        root = root.resolve()
        if root.is_dir():
            if include_root:
                d1 = cls(root.name + '/')
                dir_root.add_entry(d1)
                relroot = root.parent
            else:
                d1 = dir_root
                relroot = root

            def add_tree(d: 'Directory', path: Path) -> None:
                """ Adds the contents of the directory ``path`` to ``d`` """
                for p in path.iterdir():
                    if not any(p.match(e) for e in exclude_list):
                        parts = p.relative_to(relroot).parts
                        if p.is_dir():
                            subdir = cls('/'.join(parts) + '/')
                            d.add_entry(subdir)
                            add_tree(subdir, p)
                        else:
                            d.add_entry(File(parts, None, None))

            add_tree(d1, root)
        else:
            dir_root.add_entry(File((root.name,), None, None))
        return dir_root
