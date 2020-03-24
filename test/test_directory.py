import os
import pytest
from   check_wheel_contents.contents import Directory, File

@pytest.mark.parametrize('path', ['foo', '', os.curdir, os.pardir])
def test_constructor_path_error(path):
    with pytest.raises(ValueError) as excinfo:
        Directory(path)
    assert str(excinfo.value) \
        == f"Invalid directory path passed as Directory.path: {path!r}"

def test_default_path():
    d = Directory()
    assert d.path is None
    assert d.parts == ()

@pytest.mark.parametrize('path,expected', [
    (None, ()),
    ('foo/', ('foo',)),
    ('foo/bar/', ('foo', 'bar')),
])
def test_parts(path, expected):
    assert Directory(path).parts == expected

def test_add_entry_1level_file():
    d = Directory()
    assert not bool(d)
    assert d.entries == {}
    assert d.files == {}
    f = File.from_record_row(['foo.py', '', ''])
    d.add_entry(f)
    assert bool(d)
    assert d.entries == {"foo.py": f}
    assert d.files == {"foo.py": f}
    assert d.entries["foo.py"] is f
    assert d.files["foo.py"] is f
    assert d["foo.py"] is f

def test_add_entry_1level_dir():
    d = Directory()
    assert not bool(d)
    assert d.entries == {}
    assert d.subdirectories == {}
    sd = Directory('foo/')
    d.add_entry(sd)
    assert bool(d)
    assert d.entries == {"foo": sd}
    assert d.subdirectories == {"foo": sd}
    assert d.entries["foo"] is sd
    assert d.subdirectories["foo"] is sd
    assert d["foo"] is sd
    assert sd.entries == {}

def test_add_entry_2level_file():
    d = Directory()
    assert not bool(d)
    assert d.entries == {}
    f = File.from_record_row(['foo/bar.py', '', ''])
    d.add_entry(f)
    assert bool(d)
    assert d.entries == {
        "foo": Directory(path='foo/', entries={"bar.py": f}),
    }
    assert d.entries["foo"].entries["bar.py"] is f
    assert d["foo"]["bar.py"] is f

def test_add_entry_known_dir():
    d = Directory()
    f = File.from_record_row(['foo/bar.py', '', ''])
    d.add_entry(f)
    sd = Directory("foo/")
    d.add_entry(sd)
    assert d.entries == {
        "foo": Directory(path='foo/', entries={"bar.py": f}),
    }
    assert d.entries["foo"].entries["bar.py"] is f
    assert d["foo"]["bar.py"] is f

def test_add_entry_descendant():
    foo = Directory("foo/")
    assert not bool(foo)
    assert foo.entries == {}
    assert foo.files == {}
    f = File.from_record_row(['foo/bar.py', '', ''])
    foo.add_entry(f)
    assert bool(foo)
    assert foo.entries == {"bar.py": f}
    assert foo.files == {"bar.py": f}
    assert foo.entries["bar.py"] is f
    assert foo.files["bar.py"] is f
    assert foo["bar.py"] is f

@pytest.mark.parametrize('path', [
    'bar.py',
    'bar/baz.py',
    'bar/foo/glarch.py',
    'foo',
])
def test_add_entry_not_descendant(path):
    foo = Directory("foo/")
    f = File.from_record_row([path, '', ''])
    with pytest.raises(ValueError) as excinfo:
        foo.add_entry(f)
    assert str(excinfo.value) == f"Path {path!r} is not a descendant of 'foo/'"

def test_add_entry_nonempty_dir():
    d = Directory()
    foo = Directory('foo/')
    foo.add_entry(File.from_record_row(['foo/bar.py', '', '']))
    with pytest.raises(ValueError) as excinfo:
        d.add_entry(foo)
    assert str(excinfo.value) \
        == 'Cannot add nonempty directory to directory tree'

### Test adding multiple entries to a directory tree
### Test all_files()
