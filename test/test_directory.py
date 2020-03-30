import os
from   pathlib                       import Path
import pytest
from   check_wheel_contents.errors   import UserInputError, WheelValidationError
from   check_wheel_contents.filetree import Directory, File

def test_default_path():
    d = Directory()
    assert d.path is None
    assert d.parts == ()

@pytest.mark.parametrize('path', ['foo', '', os.curdir, os.pardir])
def test_constructor_nondir_path_error(path):
    with pytest.raises(ValueError) as excinfo:
        Directory(path)
    assert str(excinfo.value) \
        == f"Invalid directory path passed as Directory.path: {path!r}"

@pytest.mark.parametrize('path,errmsg', [
    ('/', "Absolute path in RECORD: '/'"),
    ('/foo/', "Absolute path in RECORD: '/foo/'"),
    ('foo//bar/', "Non-normalized path in RECORD: 'foo//bar/'"),
    ('./foo/', "Non-normalized path in RECORD: './foo/'"),
    ('../foo/', "Non-normalized path in RECORD: '../foo/'"),
    ('bar/./foo/', "Non-normalized path in RECORD: 'bar/./foo/'"),
    ('bar/../foo/', "Non-normalized path in RECORD: 'bar/../foo/'"),
    ('foo/./', "Non-normalized path in RECORD: 'foo/./'"),
    ('foo/../', "Non-normalized path in RECORD: 'foo/../'"),
])
def test_constructor_invalid_path(path, errmsg):
    with pytest.raises(WheelValidationError) as excinfo:
        Directory(path)
    assert str(excinfo.value) == errmsg

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
    assert "foo.py" not in d
    f = File.from_record_row(['foo.py', '', ''])
    d.add_entry(f)
    assert bool(d)
    assert d.entries == {"foo.py": f}
    assert d.files == {"foo.py": f}
    assert d.entries["foo.py"] is f
    assert d.files["foo.py"] is f
    assert d["foo.py"] is f
    assert "foo.py" in d

def test_add_entry_two_1level_files():
    d = Directory()
    assert not bool(d)
    assert d.entries == {}
    assert d.files == {}
    assert "bar.py" not in d
    f = File.from_record_row(['foo.py', '', ''])
    d.add_entry(f)
    f2 = File.from_record_row(['bar.py', '', ''])
    d.add_entry(f2)
    assert bool(d)
    assert d.entries == {"foo.py": f, "bar.py": f2}
    assert d.files == {"foo.py": f, "bar.py": f2}
    assert d.entries["bar.py"] is f2
    assert d.files["bar.py"] is f2
    assert d["bar.py"] is f2
    assert "bar.py" in d
    assert list(d.entries.keys()) == ["foo.py", "bar.py"]

def test_add_entry_1level_dir():
    d = Directory()
    assert not bool(d)
    assert d.entries == {}
    assert d.subdirectories == {}
    assert "foo" not in d
    sd = Directory('foo/')
    d.add_entry(sd)
    assert bool(d)
    assert d.entries == {"foo": sd}
    assert d.subdirectories == {"foo": sd}
    assert d.entries["foo"] is sd
    assert d.subdirectories["foo"] is sd
    assert d["foo"] is sd
    assert "foo" in d
    assert sd.entries == {}

def test_add_entry_2level_file():
    d = Directory()
    assert not bool(d)
    assert d.entries == {}
    assert "foo" not in d
    f = File.from_record_row(['foo/bar.py', '', ''])
    d.add_entry(f)
    assert bool(d)
    assert d.entries == {
        "foo": Directory(path='foo/', entries={"bar.py": f}),
    }
    assert d.entries["foo"].entries["bar.py"] is f
    assert d["foo"]["bar.py"] is f
    assert "foo" in d
    assert "bar.py" in d["foo"]

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

def test_add_entry_in_known_dir():
    d = Directory()
    f = File.from_record_row(['foo/bar.py', '', ''])
    d.add_entry(f)
    f2 = File.from_record_row(['foo/glarch.py', '', ''])
    d.add_entry(f2)
    assert d.entries == {
        "foo": Directory(path='foo/', entries={"bar.py": f, "glarch.py": f2}),
    }
    assert d.entries["foo"].entries["glarch.py"] is f2
    assert d["foo"]["glarch.py"] is f2
    assert list(d["foo"].entries.keys()) == ["bar.py", "glarch.py"]

def test_add_entry_descendant():
    foo = Directory("foo/")
    assert not bool(foo)
    assert foo.entries == {}
    assert foo.files == {}
    assert "bar.py" not in foo
    f = File.from_record_row(['foo/bar.py', '', ''])
    foo.add_entry(f)
    assert bool(foo)
    assert foo.entries == {"bar.py": f}
    assert foo.files == {"bar.py": f}
    assert foo.entries["bar.py"] is f
    assert foo.files["bar.py"] is f
    assert foo["bar.py"] is f
    assert "bar.py" in foo

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

@pytest.mark.parametrize('entry1,entry2,errpath', [
    (
        File.from_record_row(['foo', '', '']),
        Directory('foo/'),
        'foo/',
    ),
    (
        Directory('foo/'),
        File.from_record_row(['foo', '', '']),
        'foo',
    ),
    (
        File.from_record_row(['foo/bar', '', '']),
        Directory('foo/bar/'),
        'foo/bar/',
    ),
    (
        Directory('foo/bar/'),
        File.from_record_row(['foo/bar', '', '']),
        'foo/bar',
    ),
    (
        File.from_record_row(['foo', '', '']),
        File.from_record_row(['foo/bar.py', '', '']),
        'foo',
    ),
    (
        File.from_record_row(['foo/bar.py', '', '']),
        File.from_record_row(['foo', '', '']),
        'foo',
    ),
    (
        File.from_record_row(['foo', '', '']),
        Directory('foo/bar/'),
        'foo',
    ),
    (
        Directory('foo/bar/'),
        File.from_record_row(['foo', '', '']),
        'foo',
    ),
])
def test_add_entry_conflicting(entry1, entry2, errpath):
    d = Directory()
    d.add_entry(entry1)
    with pytest.raises(WheelValidationError) as excinfo:
        d.add_entry(entry2)
    assert str(excinfo.value) == f'Conflicting occurrences of path {errpath!r}'

def test_all_files():
    d = Directory()
    foo = File.from_record_row(['foo.py', '', ''])
    d.add_entry(foo)
    bar_glarch = File.from_record_row(['bar/glarch.py', '', ''])
    d.add_entry(bar_glarch)
    quux = File.from_record_row(['quux.py', '', ''])
    d.add_entry(quux)
    bar_cleesh = File.from_record_row(['bar/cleesh.py', '', ''])
    d.add_entry(bar_cleesh)
    assert d.entries == {
        "foo.py": foo,
        "bar": Directory(
            path='bar/',
            entries={"glarch.py": bar_glarch, "cleesh.py": bar_cleesh}
        ),
        "quux.py": quux,
    }
    assert list(d.entries.keys()) == ["foo.py", "bar", "quux.py"]
    assert list(d["bar"].entries.keys()) == ["glarch.py", "cleesh.py"]
    assert list(d.all_files()) == [foo, bar_glarch, bar_cleesh, quux]

@pytest.fixture
def local_tree_fs(fs):
    # fs is from pyfakefs
    fs.create_file('/var/data/foo.py')
    fs.create_file('/var/data/foo.pyc')
    fs.create_file('/var/data/bar/__init__.py')
    fs.create_file('/var/data/bar/__pycache__/__init__.cpython-36.pyc')
    fs.cwd = '/var/data'

def test_from_local_tree(local_tree_fs):
    assert Directory.from_local_tree(Path('/var/data')) == Directory(
        path=None,
        entries={
            "data": Directory(
                path='data/',
                entries={
                    "foo.py": File(('data', 'foo.py'), None, None),
                    "foo.pyc": File(('data', 'foo.pyc'), None, None),
                    "bar": Directory(
                        path='data/bar/',
                        entries={
                            "__init__.py": File(
                                ('data', 'bar', '__init__.py'),
                                None,
                                None,
                            ),
                            "__pycache__": Directory(
                                path='data/bar/__pycache__/',
                                entries={
                                    "__init__.cpython-36.pyc": File(
                                        ('data', 'bar', '__pycache__',
                                         '__init__.cpython-36.pyc'),
                                        None,
                                        None,
                                    ),
                                },
                            ),
                        },
                    ),
                },
            ),
        },
    )

def test_from_local_tree_no_include_root(local_tree_fs):
    assert Directory.from_local_tree(Path('/var/data'), include_root=False) == Directory(
        path=None,
        entries={
            "foo.py": File(('foo.py',), None, None),
            "foo.pyc": File(('foo.pyc',), None, None),
            "bar": Directory(
                path='bar/',
                entries={
                    "__init__.py": File(
                        ('bar', '__init__.py'),
                        None,
                        None,
                    ),
                    "__pycache__": Directory(
                        path='bar/__pycache__/',
                        entries={
                            "__init__.cpython-36.pyc": File(
                                ('bar', '__pycache__', '__init__.cpython-36.pyc'),
                                None,
                                None,
                            ),
                        },
                    ),
                },
            ),
        },
    )

def test_from_local_tree_exclude(local_tree_fs):
    assert Directory.from_local_tree(Path('/var/data'), exclude=['*.pyc']) == Directory(
        path=None,
        entries={
            "data": Directory(
                path='data/',
                entries={
                    "foo.py": File(('data', 'foo.py'), None, None),
                    "bar": Directory(
                        path='data/bar/',
                        entries={
                            "__init__.py": File(
                                ('data', 'bar', '__init__.py'),
                                None,
                                None,
                            ),
                            "__pycache__": Directory(
                                path='data/bar/__pycache__/',
                                entries={},
                            ),
                        },
                    ),
                },
            ),
        },
    )

def test_from_local_tree_file(local_tree_fs):
    assert Directory.from_local_tree(Path('/var/data/foo.py')) == Directory(
        path=None,
        entries={"foo.py": File(('foo.py',), None, None)},
    )

def test_from_local_tree_nonexistent(local_tree_fs):
    with pytest.raises(UserInputError) as excinfo:
        Directory.from_local_tree(Path('DNE'))
    assert str(excinfo.value) == "No such file or directory: 'DNE'"

@pytest.mark.parametrize('path,expected', [
    ('foo.py', True),
    ('bar.py', False),
    ('bar', True),
    ('bar/', True),
    ('bar/foo.py', False),
    ('bar/quux.py', False),
    ('quux.py', False),
    ('bar/bar.py', True),
    ('bar/bar.py/glarch.py', False),
    ('bar/empty', True),
    ('bar/empty/', True),
    ('bar/empty/gnusto', False),
    ('bar/empty/gnusto/', False),
    ('foo.py/', False),
    ('bar.py/bar.py/', False),
    ('project', False),
    ('project/', False),
    ('project/foo.py', False),
    ('project/bar.py', False),
    ('project/bar', False),
])
@pytest.mark.parametrize('relative', [False, True])
def test_contains_path(path, relative, expected):
    d = Directory(
        path=None,
        entries={
            "foo.py": File(('foo.py',), None, None),
            "bar": Directory(
                path='bar/',
                entries={
                    "__init__.py": File(('bar', '__init__.py'), None, None),
                    "bar.py": File(('bar', 'bar.py'), None, None),
                    "empty": Directory(path='bar/empty/'),
                },
            ),
        },
    )
    assert d.contains_path(path, relative=relative) is expected

@pytest.mark.parametrize('path,expected', [
    ('foo.py', False),
    ('bar.py', False),
    ('bar', False),
    ('bar/', False),
    ('bar/foo.py', False),
    ('bar/quux.py', False),
    ('quux.py', False),
    ('bar/bar.py', False),
    ('bar/bar.py/glarch.py', False),
    ('bar/empty', False),
    ('bar/empty/', False),
    ('bar/empty/gnusto', False),
    ('bar/empty/gnusto/', False),
    ('foo.py/', False),
    ('bar.py/bar.py/', False),
    ('bar/bar.py/', False),
    ('project', False),
    ('project/', False),
    ('project/foo.py', True),
    ('project/bar.py', False),
    ('project/bar', True),
    ('project/bar/', True),
    ('project/bar/foo.py', False),
    ('project/bar/quux.py', False),
    ('project/quux.py', False),
    ('project/bar/bar.py', True),
    ('project/bar/bar.py/glarch.py', False),
    ('project/bar/empty', True),
    ('project/bar/empty/', True),
    ('project/bar/empty/gnusto', False),
    ('project/bar/empty/gnusto/', False),
    ('project/foo.py/', False),
    ('project/bar.py/bar.py/', False),
    ('project/bar/bar.py/', False),
])
def test_contains_path_non_none_root(path, expected):
    d = Directory(
        path='project/',
        entries={
            "foo.py": File(('project', 'foo.py'), None, None),
            "bar": Directory(
                path='project/bar/',
                entries={
                    "__init__.py": File(('project', 'bar', '__init__.py'), None, None),
                    "bar.py": File(('project', 'bar', 'bar.py'), None, None),
                    "empty": Directory(path='project/bar/empty/'),
                },
            ),
        },
    )
    assert d.contains_path(path) is expected

@pytest.mark.parametrize('path,expected', [
    ('foo.py', True),
    ('bar.py', False),
    ('bar', True),
    ('bar/', True),
    ('bar/foo.py', False),
    ('bar/quux.py', False),
    ('quux.py', False),
    ('bar/bar.py', True),
    ('bar/bar.py/glarch.py', False),
    ('bar/empty', True),
    ('bar/empty/', True),
    ('bar/empty/gnusto', False),
    ('bar/empty/gnusto/', False),
    ('foo.py/', False),
    ('bar.py/bar.py/', False),
    ('bar/bar.py/', False),
    ('project', False),
    ('project/', False),
    ('project/foo.py', False),
    ('project/bar.py', False),
    ('project/bar', False),
    ('project/bar/', False),
    ('project/bar/foo.py', False),
    ('project/bar/quux.py', False),
    ('project/quux.py', False),
    ('project/bar/bar.py', False),
    ('project/bar/bar.py/glarch.py', False),
    ('project/bar/empty', False),
    ('project/bar/empty/', False),
    ('project/bar/empty/gnusto', False),
    ('project/bar/empty/gnusto/', False),
    ('project/foo.py/', False),
    ('project/bar.py/bar.py/', False),
    ('project/bar/bar.py/', False),
])
def test_contains_path_non_none_root_relative(path, expected):
    d = Directory(
        path='project/',
        entries={
            "foo.py": File(('project', 'foo.py'), None, None),
            "bar": Directory(
                path='project/bar/',
                entries={
                    "__init__.py": File(('project', 'bar', '__init__.py'), None, None),
                    "bar.py": File(('project', 'bar', 'bar.py'), None, None),
                    "empty": Directory(path='project/bar/empty/'),
                },
            ),
        },
    )
    assert d.contains_path(path, relative=True) is expected
