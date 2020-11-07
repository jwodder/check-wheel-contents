from   collections      import defaultdict
import csv
from   io               import TextIOWrapper
import os
import re
from   typing           import DefaultDict, Iterable, List, Optional, TextIO, \
                                    Tuple, Union
from   zipfile          import ZipFile
import attr
from   property_manager import cached_property
from   wheel_filename   import parse_wheel_filename
from   .errors          import WheelValidationError
from   .filetree        import Directory, File
from   .util            import find_wheel_dirs, is_data_dir, is_dist_info_dir

ROOT_IS_PURELIB_RGX = re.compile(r'Root-Is-Purelib\s*:\s*(.*?)\s*', flags=re.I)

@attr.s(auto_attribs=True)
class WheelContents:
    """ Representation of the contents of a wheel """

    #: The name of the wheel's ``.dist-info`` directory
    dist_info_dir: str = attr.ib()
    #: The name of the wheel's ``.data`` directory, if any
    data_dir: str = attr.ib()
    #: The value of the :mailheader:`Root-Is-Purelib` field in the
    #: :file:`WHEEL` file
    root_is_purelib: bool = attr.ib(default=True)
    #: A mapping from ``File.signature`` values to lists of the `File` objects
    #: with those values
    by_signature: DefaultDict[Tuple[Optional[int], Optional[str]], List[File]] \
        = attr.ib(factory=lambda: defaultdict(list))
    #: The wheel's file tree
    filetree: Directory = attr.ib(factory=Directory)

    @cached_property
    def purelib_tree(self) -> Directory:
        """
        The subtree of the wheel's file tree corresponding to the purelib
        section.  The returned `Directory`'s ``path`` is `None` if
        ``root_is_purelib`` is true; otherwise, the ``path`` is
        ``{self.data_dir}/purelib/``.
        """
        if self.root_is_purelib:
            return Directory(
                path=None,
                entries={
                    k:v for k,v in self.filetree.entries.items()
                    if k not in (self.dist_info_dir, self.data_dir)
                },
            )
        else:
            try:
                purelib = self.filetree[self.data_dir]['purelib']  # type: ignore
            except (KeyError, TypeError):
                return Directory(f'{self.data_dir}/purelib/')
            else:
                assert isinstance(purelib, Directory)
                return purelib

    @cached_property
    def platlib_tree(self) -> Directory:
        """
        The subtree of the wheel's file tree corresponding to the platlib
        section.  The returned `Directory`'s ``path`` is `None` if
        ``root_is_purelib`` is false; otherwise, the ``path`` is
        ``{self.data_dir}/platlib/``.
        """
        if not self.root_is_purelib:
            return Directory(
                path=None,
                entries={
                    k:v for k,v in self.filetree.entries.items()
                    if k not in (self.dist_info_dir, self.data_dir)
                },
            )
        else:
            try:
                platlib = self.filetree[self.data_dir]['platlib']  # type: ignore
            except (KeyError, TypeError):
                return Directory(f'{self.data_dir}/platlib/')
            else:
                assert isinstance(platlib, Directory)
                return platlib

    @classmethod
    def from_wheel(cls, path: Union[str, os.PathLike]) -> 'WheelContents':
        """ Construct a `WheelContents` from the wheel at the given path """
        whlname = parse_wheel_filename(path)
        with open(path, 'rb') as fp, ZipFile(fp) as zf:
            dist_info_dir, data_dir = find_wheel_dirs(
                zf.namelist(),
                whlname.project,
                whlname.version,
            )
            if data_dir is None:
                data_dir = f'{whlname.project}-{whlname.version}.data'
            wc = cls(dist_info_dir=dist_info_dir, data_dir=data_dir)
            try:
                wheel_info = zf.getinfo(f'{dist_info_dir}/WHEEL')
            except KeyError:
                raise WheelValidationError('No WHEEL file in wheel')
            with zf.open(wheel_info) as wf:
                for line in TextIOWrapper(wf, 'utf-8'):
                    m = ROOT_IS_PURELIB_RGX.fullmatch(line)
                    if m:
                        rip = m.group(1)
                        if rip.lower() == 'true':
                            wc.root_is_purelib = True
                        elif rip.lower() == 'false':
                            wc.root_is_purelib = False
                        else:
                            raise WheelValidationError(
                                f'Invalid Root-Is-Purelib value in WHEEL'
                                f' file: {rip!r}'
                            )
                        break
                else:
                    raise WheelValidationError(
                        'Root-Is-Purelib header not found in WHEEL file'
                    )
            try:
                record_info = zf.getinfo(f'{dist_info_dir}/RECORD')
            except KeyError:
                raise WheelValidationError('No RECORD file in wheel')
            with zf.open(record_info) as rf:
                wc.add_record_file(TextIOWrapper(rf, 'utf-8', newline=''))
        wc.validate_tree()
        return wc

    def add_record_file(self, fp: TextIO) -> None:
        """
        Add the files & directories described by the given :file:`RECORD` file
        to the `WheelContents`
        """
        self.add_record_rows(csv.reader(fp, delimiter=',', quotechar='"'))

    def add_record_rows(self, rows: Iterable[List[str]]) -> None:
        """
        Add the files & directories described by the rows of fields read from a
        wheel's :file:`RECORD` file to the `WheelContents`
        """
        for row in rows:
            entry: Union[File, Directory]
            if row and row[0].endswith('/'):
                entry = Directory(row[0])
            else:
                entry = File.from_record_row(row)
            self.add_entry(entry)

    def add_entry(self, entry: Union['File', 'Directory']) -> None:
        """ Add a `File` or `Directory` to the `WheelContents`' file tree """
        self.filetree.add_entry(entry)
        if isinstance(entry, File):
            self.by_signature[entry.signature].append(entry)
        # Invalidate cached properties:
        del self.purelib_tree
        del self.platlib_tree

    def validate_tree(self) -> None:
        """
        Check that various assumptions about the `WheelContents` hold, raising
        a `WheelValidationError` if any of them fail
        """
        # The discussion at <https://discuss.python.org/t/3764> says that it's
        # OK to expect no more than one .dist-info or .data directory in a
        # wheel.
        dist_info_dirs = [
            name for name in self.filetree.subdirectories.keys()
                 if is_dist_info_dir(name)
        ]
        if len(dist_info_dirs) > 1:
            raise WheelValidationError(
                'Wheel contains multiple .dist-info directories in RECORD'
            )
        elif len(dist_info_dirs) == 1 \
                and dist_info_dirs[0] != self.dist_info_dir:
            raise WheelValidationError(
                f".dist-info directory in RECORD ({dist_info_dirs[0]!r}) does"
                f" not match actual directory name ({self.dist_info_dir!r})"
            )
        elif not dist_info_dirs:
            raise WheelValidationError('No .dist-info directory in RECORD')
        data_dirs = [
            name for name in self.filetree.subdirectories.keys()
                 if is_data_dir(name)
        ]
        if len(data_dirs) > 1:
            raise WheelValidationError(
                'Wheel contains multiple .data directories in RECORD'
            )
        elif len(data_dirs) == 1 and data_dirs[0] != self.data_dir:
            raise WheelValidationError(
                f".data directory in RECORD ({data_dirs[0]!r}) does"
                f" not match actual directory name ({self.data_dir!r})"
            )
        if self.data_dir in self.filetree:
            if self.root_is_purelib:
                if "purelib" in self.filetree[self.data_dir]:  # type: ignore
                    raise WheelValidationError(
                        'Wheel is purelib yet contains *.data/purelib'
                    )
                try:
                    platlib = self.filetree[self.data_dir]["platlib"]  # type: ignore
                except KeyError:
                    pass
                else:
                    if not isinstance(platlib, Directory):
                        raise WheelValidationError(
                            '*.data/platlib is not a directory'
                        )
            else:
                if "platlib" in self.filetree[self.data_dir]:  # type: ignore
                    raise WheelValidationError(
                        'Wheel is platlib yet contains *.data/platlib'
                    )
                try:
                    purelib = self.filetree[self.data_dir]["purelib"]  # type: ignore
                except KeyError:
                    pass
                else:
                    if not isinstance(purelib, Directory):
                        raise WheelValidationError(
                            '*.data/purelib is not a directory'
                        )
