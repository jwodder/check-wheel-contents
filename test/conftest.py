from   pathlib               import Path
from   pyfakefs.fake_pathlib import FakePath
import pytest

# Path somehow gets monkeypatched during testing, so in order to have access
# to the original class we'll simply create an instance of it
PATH = object.__new__(Path)

@pytest.fixture
def faking_path(monkeypatch):
    # Monkeypatch Path.__eq__ so that pyfakefs FakePaths compare equal to real
    # pathlib.Paths
    # <https://github.com/jmcgeheeiv/pyfakefs/issues/478#issuecomment-487492775>
    def path_eq(self, other):
        Path = type(PATH)
        if isinstance(other, (Path, FakePath)):
            return str(self) == str(other)
        return super(Path, self).__eq__(other)
    monkeypatch.setattr(type(PATH), '__eq__', path_eq)
