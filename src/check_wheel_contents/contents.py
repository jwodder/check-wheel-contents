from   collections      import defaultdict
import csv
from   io               import TextIOWrapper
import os
from   os.path          import basename
import re
from   typing           import DefaultDict, List, Tuple, Union
from   zipfile          import ZipFile
import attr
from   property_manager import cached_property
from   wheel_filename   import parse_wheel_filename
from   .errors          import WheelValidationError
from   .filetree        import Directory, File
from   .util            import is_data_dir, is_dist_info_dir

ROOT_IS_PURELIB_RGX = re.compile(r'Root-Is-Purelib\s*:\s*(.*?)\s*', flags=re.I)

@attr.s(auto_attribs=True)
class WheelContents:
    dist_info_dir: str = attr.ib()
    data_dir: str = attr.ib()
    root_is_purelib: bool = attr.ib(default=True)
    by_signature: DefaultDict[Tuple[int, str], List[File]] \
        = attr.ib(factory=lambda: defaultdict(list))
    filetree: Directory = attr.ib(factory=Directory)

    @cached_property
    def purelib_tree(self):
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
                return self.filetree[self.data_dir]['purelib']
            except (KeyError, TypeError):
                return Directory(f'{self.data_dir}/purelib/')

    @cached_property
    def platlib_tree(self):
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
                return self.filetree[self.data_dir]['platlib']
            except (KeyError, TypeError):
                return Directory(f'{self.data_dir}/platlib/')

    @classmethod
    def from_wheel(cls, path: Union[str, os.PathLike]):
        whlname = parse_wheel_filename(basename(path))
        dist_info_dir = f'{whlname.project}-{whlname.version}.dist-info'
        data_dir = f'{whlname.project}-{whlname.version}.data'
        wc = cls(dist_info_dir=dist_info_dir, data_dir=data_dir)
        with open(path, 'rb') as fp, ZipFile(fp) as zf:
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

    def add_record_file(self, fp):
        self.add_record_rows(csv.reader(fp, delimiter=',', quotechar='"'))

    def add_record_rows(self, rows):
        for row in rows:
            if row and row[0].endswith('/'):
                entry = Directory(row[0])
            else:
                entry = File.from_record_row(row)
            self.add_entry(entry)

    def add_entry(self, entry: Union['File', 'Directory']):
        self.filetree.add_entry(entry)
        if isinstance(entry, File):
            self.by_signature[entry.signature].append(entry)
        # Invalidate cached properties:
        del self.purelib_tree
        del self.platlib_tree

    def validate_tree(self) -> None:
        # The discussion at <https://discuss.python.org/t/3764> says that it's
        # OK to expect no more than one .dist-info or .data directory in a
        # wheel.
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
        elif not dist_info_dirs:
            raise WheelValidationError('No .dist-info directory in wheel')
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
        if self.data_dir in self.filetree:
            if self.root_is_purelib:
                if "purelib" in self.filetree[self.data_dir]:
                    raise WheelValidationError(
                        'Wheel is purelib yet contains *.data/purelib'
                    )
                try:
                    platlib = self.filetree[self.data_dir]["platlib"]
                except KeyError:
                    pass
                else:
                    if not isinstance(platlib, Directory):
                        raise WheelValidationError(
                            '*.data/platlib is not a directory'
                        )
            else:
                if "platlib" in self.filetree[self.data_dir]:
                    raise WheelValidationError(
                        'Wheel is platlib yet contains *.data/platlib'
                    )
                try:
                    purelib = self.filetree[self.data_dir]["purelib"]
                except KeyError:
                    pass
                else:
                    if not isinstance(purelib, Directory):
                        raise WheelValidationError(
                            '*.data/purelib is not a directory'
                        )
