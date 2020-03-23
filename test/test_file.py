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

@pytest.mark.parametrize('prefix,prebool', [
    ('', True),
    ('foo-1.0.dist-info/', False),
    ('foo-1.0.data/purelib/', True),
    ('foo-1.0.data/platlib/', True),
    ('foo-1.0.data/data/', False),
    ('foo-1.0.data/scripts/', False),
    ('foo-1.0.data/headers/', False),
])
@pytest.mark.parametrize('path,pathbool', [
    ('foo.py', True),
    ('foo-1.0.data/purelib', False),
    ('foo-1.0.data/platlib', False),
    ('foo/__init__.py', True),
    ('foo/bar.py', True),
    ('foo/__init__', False),
    ('foo.py/bar.py', False),
    ('def.py', False),
    ('foo_bar.py', True),
    ('foo-bar.py', False),
    ('foo_bar/baz.py', True),
    ('foo-bar/baz.py', False),
])
def test_is_valid_module_path(prefix, path, prebool, pathbool):
    f = File.from_record_row([prefix+path, None, None])
    assert f.is_valid_module_path() is (prebool and pathbool)
