import pytest
from   check_wheel_contents.contents import File

@pytest.mark.parametrize('path,expected', [
    ('somepackage.py', ('somepackage.py',)),
    ('somepackage/foo.py', ('somepackage', 'foo.py')),
    ('README.txt', ('README.txt',)),
    ('METADATA', ('METADATA',)),
    ('somepackage-1.0.0.dist-info/METADATA', None),
    ('somepackage-1.0.0.dist-info/somepackage.py', None),
    ('somepackage-1.0.0.data/data/etc/nfp.ini', None),
    ('somepackage-1.0.0.data/scripts/rst2html.py', None),
    ('somepackage-1.0.0.data/headers/greenlet.h', None),
    (
        'somepackage-1.0.0.data/purelib/somepackage/__init__.py',
        ('somepackage', '__init__.py'),
    ),
    (
        f'somepackage-1.0.0.data/platlib/somepackage/__init__.py',
        ('somepackage', '__init__.py'),
    ),
    ('somepackage-1.0.0.data/purelib', None),
    ('somepackage-1.0.0.data/platlib', None),
    (
        'somepackage.data/data/etc/config.ini',
        ('somepackage.data', 'data', 'etc', 'config.ini'),
    ),
    (
        'somepackage.dist-info/RECORD',
        ('somepackage.dist-info', 'RECORD'),
    ),
    (
        'somepackage-0.1.0-1.data/data/etc/config.ini',
        ('somepackage-0.1.0-1.data', 'data', 'etc', 'config.ini'),
    ),
    (
        'somepackage-0.1.0-1.dist-info/RECORD',
        ('somepackage-0.1.0-1.dist-info', 'RECORD'),
    ),
])
def test_libparts(path, expected):
    assert File.from_record_row([path, None, None]).libparts == expected
