import pytest
from   check_wheel_contents.contents import Section, WheelContents

WHEEL_NAME_VERSION = 'somepackage-1.0.0'
DIST_INFO_DIR      = f'{WHEEL_NAME_VERSION}.dist-info'
DATA_DIR           = f'{WHEEL_NAME_VERSION}.data'

@pytest.mark.parametrize('path,section,libpath', [
    ('somepackage.py', Section.PURELIB, ('somepackage.py',)),
    ('somepackage/foo.py', Section.PURELIB, ('somepackage', 'foo.py')),
    ('README.txt', Section.PURELIB, ('README.txt',)),
    ('METADATA', Section.PURELIB, ('METADATA',)),
    (f'{DIST_INFO_DIR}/METADATA', Section.DIST_INFO, None),
    (f'{DIST_INFO_DIR}/somepackage.py', Section.DIST_INFO, None),
    (f'{DATA_DIR}/data/etc/nfp.ini', Section.MISC_DATA, None),
    (f'{DATA_DIR}/scripts/rst2html.py', Section.MISC_DATA, None),
    (f'{DATA_DIR}/headers/greenlet.h', Section.MISC_DATA, None),
    (
        f'{DATA_DIR}/purelib/somepackage/__init__.py',
        Section.PURELIB,
        ('somepackage', '__init__.py'),
    ),
    (
        f'{DATA_DIR}/platlib/somepackage/__init__.py',
        Section.PLATLIB,
        ('somepackage', '__init__.py'),
    ),
    (f'{DATA_DIR}/purelib', Section.MISC_DATA, None),
    (f'{DATA_DIR}/platlib', Section.MISC_DATA, None),
    (
        f'somepackage.data/data/etc/config.ini',
        Section.PURELIB,
        ('somepackage.data', 'data', 'etc', 'config.ini'),
    ),
    (
        f'somepackage.dist-info/RECORD',
        Section.PURELIB,
        ('somepackage.dist-info', 'RECORD'),
    ),
    (
        f'otherpackage-0.1.0.data/data/etc/config.ini',
        Section.PURELIB,
        ('otherpackage-0.1.0.data', 'data', 'etc', 'config.ini'),
    ),
    (
        f'otherpackage-0.1.0.dist-info/RECORD',
        Section.PURELIB,
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
    ('somepackage.py', Section.PLATLIB, ('somepackage.py',)),
    ('somepackage/foo.py', Section.PLATLIB, ('somepackage', 'foo.py')),
    ('README.txt', Section.PLATLIB, ('README.txt',)),
    ('METADATA', Section.PLATLIB, ('METADATA',)),
    (f'{DIST_INFO_DIR}/METADATA', Section.DIST_INFO, None),
    (f'{DIST_INFO_DIR}/somepackage.py', Section.DIST_INFO, None),
    (f'{DATA_DIR}/data/etc/nfp.ini', Section.MISC_DATA, None),
    (f'{DATA_DIR}/scripts/rst2html.py', Section.MISC_DATA, None),
    (f'{DATA_DIR}/headers/greenlet.h', Section.MISC_DATA, None),
    (
        f'{DATA_DIR}/purelib/somepackage/__init__.py',
        Section.PURELIB,
        ('somepackage', '__init__.py'),
    ),
    (
        f'{DATA_DIR}/platlib/somepackage/__init__.py',
        Section.PLATLIB,
        ('somepackage', '__init__.py'),
    ),
    (f'{DATA_DIR}/purelib', Section.MISC_DATA, None),
    (f'{DATA_DIR}/platlib', Section.MISC_DATA, None),
    (
        f'somepackage.data/data/etc/config.ini',
        Section.PLATLIB,
        ('somepackage.data', 'data', 'etc', 'config.ini'),
    ),
    (
        f'somepackage.dist-info/RECORD',
        Section.PLATLIB,
        ('somepackage.dist-info', 'RECORD'),
    ),
    (
        f'otherpackage-0.1.0.data/data/etc/config.ini',
        Section.PLATLIB,
        ('otherpackage-0.1.0.data', 'data', 'etc', 'config.ini'),
    ),
    (
        f'otherpackage-0.1.0.dist-info/RECORD',
        Section.PLATLIB,
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
