import pytest
from   check_wheel_contents.contents import FileSection, WheelContents

WHEEL_NAME_VERSION = 'somepackage-1.0.0'
DIST_INFO_DIR      = f'{WHEEL_NAME_VERSION}.dist-info'
DATA_DIR           = f'{WHEEL_NAME_VERSION}.data'

@pytest.mark.parametrize('path,section,libpath', [
    ('somepackage.py', FileSection.PURELIB, ('somepackage.py',)),
    ('somepackage/foo.py', FileSection.PURELIB, ('somepackage', 'foo.py')),
    ('README.txt', FileSection.PURELIB, ('README.txt',)),
    ('METADATA', FileSection.PURELIB, ('METADATA',)),
    (f'{DIST_INFO_DIR}/METADATA', FileSection.DIST_INFO, None),
    (f'{DIST_INFO_DIR}/somepackage.py', FileSection.DIST_INFO, None),
    (f'{DATA_DIR}/data/etc/nfp.ini', FileSection.MISC_DATA, None),
    (f'{DATA_DIR}/scripts/rst2html.py', FileSection.MISC_DATA, None),
    (f'{DATA_DIR}/headers/greenlet.h', FileSection.MISC_DATA, None),
    (
        f'{DATA_DIR}/purelib/somepackage/__init__.py',
        FileSection.PURELIB,
        ('somepackage', '__init__.py'),
    ),
    (
        f'{DATA_DIR}/platlib/somepackage/__init__.py',
        FileSection.PLATLIB,
        ('somepackage', '__init__.py'),
    ),
    (f'{DATA_DIR}/purelib', FileSection.MISC_DATA, None),
    (f'{DATA_DIR}/platlib', FileSection.MISC_DATA, None),
    (
        f'somepackage.data/data/etc/config.ini',
        FileSection.PURELIB,
        ('somepackage.data', 'data', 'etc', 'config.ini'),
    ),
    (
        f'somepackage.dist-info/RECORD',
        FileSection.PURELIB,
        ('somepackage.dist-info', 'RECORD'),
    ),
    (
        f'otherpackage-0.1.0.data/data/etc/config.ini',
        FileSection.PURELIB,
        ('otherpackage-0.1.0.data', 'data', 'etc', 'config.ini'),
    ),
    (
        f'otherpackage-0.1.0.dist-info/RECORD',
        FileSection.PURELIB,
        ('otherpackage-0.1.0.dist-info', 'RECORD'),
    ),
])
def test_categorize_path_root_is_purelib(path, section, libpath):
    whlcon = WheelContents(
        dist_info_dir   = DIST_INFO_DIR,
        data_dir        = DATA_DIR,
        root_is_purelib = True,
    )
    assert whlcon.categorize_path(path) == (section, libpath)

@pytest.mark.parametrize('path,section,libpath', [
    ('somepackage.py', FileSection.PLATLIB, ('somepackage.py',)),
    ('somepackage/foo.py', FileSection.PLATLIB, ('somepackage', 'foo.py')),
    ('README.txt', FileSection.PLATLIB, ('README.txt',)),
    ('METADATA', FileSection.PLATLIB, ('METADATA',)),
    (f'{DIST_INFO_DIR}/METADATA', FileSection.DIST_INFO, None),
    (f'{DIST_INFO_DIR}/somepackage.py', FileSection.DIST_INFO, None),
    (f'{DATA_DIR}/data/etc/nfp.ini', FileSection.MISC_DATA, None),
    (f'{DATA_DIR}/scripts/rst2html.py', FileSection.MISC_DATA, None),
    (f'{DATA_DIR}/headers/greenlet.h', FileSection.MISC_DATA, None),
    (
        f'{DATA_DIR}/purelib/somepackage/__init__.py',
        FileSection.PURELIB,
        ('somepackage', '__init__.py'),
    ),
    (
        f'{DATA_DIR}/platlib/somepackage/__init__.py',
        FileSection.PLATLIB,
        ('somepackage', '__init__.py'),
    ),
    (f'{DATA_DIR}/purelib', FileSection.MISC_DATA, None),
    (f'{DATA_DIR}/platlib', FileSection.MISC_DATA, None),
    (
        f'somepackage.data/data/etc/config.ini',
        FileSection.PLATLIB,
        ('somepackage.data', 'data', 'etc', 'config.ini'),
    ),
    (
        f'somepackage.dist-info/RECORD',
        FileSection.PLATLIB,
        ('somepackage.dist-info', 'RECORD'),
    ),
    (
        f'otherpackage-0.1.0.data/data/etc/config.ini',
        FileSection.PLATLIB,
        ('otherpackage-0.1.0.data', 'data', 'etc', 'config.ini'),
    ),
    (
        f'otherpackage-0.1.0.dist-info/RECORD',
        FileSection.PLATLIB,
        ('otherpackage-0.1.0.dist-info', 'RECORD'),
    ),
])
def test_categorize_path_root_is_platlib(path, section, libpath):
    whlcon = WheelContents(
        dist_info_dir   = DIST_INFO_DIR,
        data_dir        = DATA_DIR,
        root_is_purelib = False,
    )
    assert whlcon.categorize_path(path) == (section, libpath)
