import pytest
from   check_wheel_contents.errors   import WheelValidationError
from   check_wheel_contents.filetree import File

@pytest.mark.parametrize('row,expected', [
    (['foo.py', '', ''], File(parts=('foo.py',), size=None, hashsum=None)),
    (['foo.py', '', '42'], File(parts=('foo.py',), size=42, hashsum=None)),
    (
        ['foo.py', 'sha256=...', ''],
        File(parts=('foo.py',), size=None, hashsum='sha256=...'),
    ),
    (
        ['foo.py', 'sha256=...', '42'],
        File(parts=('foo.py',), size=42, hashsum='sha256=...'),
    ),
    (
        ['foo/bar.py', '', ''],
        File(parts=('foo', 'bar.py'), size=None, hashsum=None),
    ),
])
def test_from_record_row(row, expected):
    assert File.from_record_row(row) == expected

@pytest.mark.parametrize('row', [
    [],
    ['foo.py'],
    ['foo.py', 'sha256=...'],
    ['foo.py', 'sha256=...', '42', 'stuff'],
    ['foo.py', '42', 'sha256=...'],
    ['foo.py', 'sha256=...', '42a'],
])
def test_from_record_row_bad_row(row):
    with pytest.raises(WheelValidationError) as excinfo:
        File.from_record_row(row)
    assert str(excinfo.value) == f'Invalid RECORD entry: {row!r}'

def test_from_record_row_dirpath_error():
    with pytest.raises(ValueError) as excinfo:
        File.from_record_row(['foo/', '', ''])
    assert str(excinfo.value) \
        == "Invalid file path passed to File.from_record_row(): 'foo/'"

@pytest.mark.parametrize('path,errmsg', [
    ('', "Empty path in RECORD"),
    ('/foo.py', "Absolute path in RECORD: '/foo.py'"),
    ('foo//bar.py', "Non-normalized path in RECORD: 'foo//bar.py'"),
    ('./foo.py', "Non-normalized path in RECORD: './foo.py'"),
    ('../foo.py', "Non-normalized path in RECORD: '../foo.py'"),
    ('bar/./foo.py', "Non-normalized path in RECORD: 'bar/./foo.py'"),
    ('bar/../foo.py', "Non-normalized path in RECORD: 'bar/../foo.py'"),
    ('foo/.', "Non-normalized path in RECORD: 'foo/.'"),
    ('foo/..', "Non-normalized path in RECORD: 'foo/..'"),
])
def test_from_record_row_path_validation_error(path, errmsg):
    with pytest.raises(WheelValidationError) as excinfo:
        File.from_record_row([path, '', ''])
    assert str(excinfo.value) == errmsg

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
        'somepackage-1.0.0.data/platlib/somepackage/__init__.py',
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
    assert File.from_record_row([path, '', '']).libparts == expected

@pytest.mark.parametrize('path,expected', [
    ('somepackage.py', 'somepackage.py'),
    ('somepackage/foo.py', 'somepackage/foo.py'),
    ('README.txt', 'README.txt'),
    ('METADATA', 'METADATA'),
    ('somepackage-1.0.0.dist-info/METADATA', None),
    ('somepackage-1.0.0.dist-info/somepackage.py', None),
    ('somepackage-1.0.0.data/data/etc/nfp.ini', None),
    ('somepackage-1.0.0.data/scripts/rst2html.py', None),
    ('somepackage-1.0.0.data/headers/greenlet.h', None),
    (
        'somepackage-1.0.0.data/purelib/somepackage/__init__.py',
        'somepackage/__init__.py',
    ),
    (
        'somepackage-1.0.0.data/platlib/somepackage/__init__.py',
        'somepackage/__init__.py',
    ),
    ('somepackage-1.0.0.data/purelib', None),
    ('somepackage-1.0.0.data/platlib', None),
    (
        'somepackage.data/data/etc/config.ini',
        'somepackage.data/data/etc/config.ini',
    ),
    (
        'somepackage.dist-info/RECORD',
        'somepackage.dist-info/RECORD',
    ),
    (
        'somepackage-0.1.0-1.data/data/etc/config.ini',
        'somepackage-0.1.0-1.data/data/etc/config.ini',
    ),
    (
        'somepackage-0.1.0-1.dist-info/RECORD',
        'somepackage-0.1.0-1.dist-info/RECORD',
    ),
])
def test_libpath(path, expected):
    assert File.from_record_row([path, '', '']).libpath == expected

@pytest.mark.parametrize('path,expected', [
    ('foo.py', True),
    ('FOO.PY', False),
    ('foo.pyc', False),
    ('foo.pyo', False),
    ('foo/bar.py', True),
    ('foo.py/bar', False),
    ('foo/.py', False),
    ('foo/py', False),
    ('not-an-identifier.py', True),
    ('def.py', True),
    ('extra.ext.py', True),
    ('foo.cpython-38-x86_64-linux-gnu.so', True),
    ('graph.cpython-37m-darwin.so', True),
    ('foo.cp38-win_amd64.pyd', True),
    ('foo.cp38-win32.pyd', True),
    ('foo.so', True),
    ('foo.pyd', True),
    ('_ffi.abi3.so', True),
])
def test_has_module_ext(path, expected):
    assert File.from_record_row([path, '', '']).has_module_ext() is expected

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
    f = File.from_record_row([prefix+path, '', ''])
    assert f.is_valid_module_path() is (prebool and pathbool)

@pytest.mark.parametrize('path,ext', [
    ('foo.py', '.py'),
    ('FOO.PY', '.PY'),
    ('foo.pyc', '.pyc'),
    ('foo.pyo', '.pyo'),
    ('foo/bar.py', '.py'),
    ('foo.py/bar', ''),
    ('foo/.py', ''),
    ('foo/py', ''),
    ('extra.ext.py', '.py'),
    ('foo.cpython-38-x86_64-linux-gnu.so', '.so'),
    ('graph.cpython-37m-darwin.so', '.so'),
    ('foo.cp38-win_amd64.pyd', '.pyd'),
    ('foo.cp38-win32.pyd', '.pyd'),
    ('foo.so', '.so'),
    ('foo.pyd', '.pyd'),
    ('_ffi.abi3.so', '.so'),
])
def test_extension(path, ext):
    assert File.from_record_row([path, '', '']).extension == ext

def test_signature():
    assert File.from_record_row(['foo.py', 'sha256=abc', '42']).signature \
        == (42, 'sha256=abc')

@pytest.mark.parametrize('path,parts', [
    ('foo.py', ('foo.py',)),
    ('foo/bar.py', ('foo', 'bar.py')),
    ('foo.py/bar.py', ('foo.py', 'bar.py')),
    ('foo/bar/baz', ('foo', 'bar', 'baz')),
])
def test_str_path_parts(path, parts):
    f = File.from_record_row([path, '', ''])
    assert str(f) == path
    assert f.path == path
    assert f.parts == parts
