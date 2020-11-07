import base64
import hashlib
from   keyword         import iskeyword
import re
from   typing          import List, Optional, Tuple
from   packaging.utils import canonicalize_name, canonicalize_version
from   .errors         import WheelValidationError

# <https://discuss.python.org/t/identifying-parsing-binary-extension-filenames/>
MODULE_EXT_RGX = re.compile(
    r'(?<=.)\.(?:py|pyd|so|[-A-Za-z0-9_]+\.(?:pyd|so))\Z'
)

DIST_INFO_DIR_RGX = re.compile(
    r'[A-Za-z0-9](?:[A-Za-z0-9._]*[A-Za-z0-9])?-[A-Za-z0-9_.!+]+\.dist-info'
)

DATA_DIR_RGX = re.compile(
    r'[A-Za-z0-9](?:[A-Za-z0-9._]*[A-Za-z0-9])?-[A-Za-z0-9_.!+]+\.data'
)

def comma_split(s: str) -> List[str]:
    """
    Split apart a string on commas, discarding leading & trailing whitespace
    from all parts and discarding empty parts
    """
    return [k for k in map(str.strip, s.split(',')) if k]

def bytes_signature(b: bytes) -> Tuple[int, str]:
    return (
        len(b),
        'sha256=' + urlsafe_b64encode_nopad(hashlib.sha256(b).digest()),
    )

def urlsafe_b64encode_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('us-ascii')

def pymodule_basename(filename: str) -> Optional[str]:
    """
    If ``filename`` (a filename without any directory components) has a file
    extension indicating it is a Python module (either source or binary
    extension), return the part before the extension; otherwise, return `None`.
    """
    m = MODULE_EXT_RGX.search(filename)
    if m is not None:
        return filename[:m.start()]
    else:
        return None

def is_dist_info_dir(name: str) -> bool:
    return DIST_INFO_DIR_RGX.fullmatch(name) is not None

def is_data_dir(name: str) -> bool:
    return DATA_DIR_RGX.fullmatch(name) is not None

def validate_path(path: str) -> None:
    if path.startswith('/'):
        raise WheelValidationError(f'Absolute path in RECORD: {path!r}')
    elif path == '':
        raise WheelValidationError('Empty path in RECORD')
    elif '//' in path:
        raise WheelValidationError(f'Non-normalized path in RECORD: {path!r}')
    parts = path.split('/')
    if '.' in parts or '..' in parts:
        raise WheelValidationError(f'Non-normalized path in RECORD: {path!r}')

def is_stubs_dir(name: str) -> bool:
    if not name.endswith('-stubs'):
        return False
    basename = name[:-6]
    return basename.isidentifier() and not iskeyword(basename)

def find_wheel_dirs(namelist: List[str], project: str, version: str) \
        -> Tuple[str, Optional[str]]:
    """
    Given a list ``namelist`` of files in a wheel for a project ``project`` and
    version ``version``, find & return the name of the wheel's ``.dist-info``
    directory and (if it has one) its ``.data`` directory.

    :raises WheelValidationError: if there is no unique ``.dist-info``
        directory in the input
    :raises WheelValidationError: if the name & version of the ``.dist-info``
        directory are not normalization-equivalent to ``project`` & ``version``
    :raises WheelValidationError: if there is more than one ``.data`` directory
        in the input
    :raises WheelValidationError: if the name & version of the ``.data``
        directory are not normalization-equivalent to ``project`` & ``version``
    """
    canon_project = canonicalize_name(project)
    canon_version = canonicalize_version(version.replace('_', '-'))
    dist_info_dirs = set()
    data_dirs = set()
    for n in namelist:
        basename = n.rstrip('/').split('/')[0]
        if is_dist_info_dir(basename):
            dist_info_dirs.add(basename)
        if is_data_dir(basename):
            data_dirs.add(basename)
    if len(dist_info_dirs) > 1:
        raise WheelValidationError(
            'Wheel contains multiple .dist-info directories'
        )
    elif len(dist_info_dirs) == 1:
        dist_info_dir = next(iter(dist_info_dirs))
        diname, _, diversion = dist_info_dir[:-len(".dist-info")].partition('-')
        if (
            canonicalize_name(diname) != canon_project
            or canonicalize_version(diversion.replace('_', '-'))
                != canon_version
        ):
            raise WheelValidationError(
                f"Project & version of wheel's .dist-info directory do not"
                f" match wheel name: {dist_info_dir!r}"
            )
    else:
        raise WheelValidationError('No .dist-info directory in wheel')
    data_dir: Optional[str]
    if len(data_dirs) > 1:
        raise WheelValidationError('Wheel contains multiple .data directories')
    elif len(data_dirs) == 1:
        data_dir = next(iter(data_dirs))
        daname, _, daversion = data_dir[:-len(".data")].partition('-')
        if (
            canonicalize_name(daname) != canon_project
            or canonicalize_version(daversion.replace('_', '-'))
                != canon_version
        ):
            raise WheelValidationError(
                f"Project & version of wheel's .data directory do not match"
                f" wheel name: {data_dir!r}"
            )
    else:
        data_dir = None
    return (dist_info_dir, data_dir)
