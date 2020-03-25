from   enum    import Enum
from   typing  import List, Optional, Set
import attr
from   .errors import UserInputError
from   .util   import comma_split

class Check(Enum):
    W001 = 'Wheel contains .pyc/.pyo files'
    W002 = 'Wheel contains duplicate files'
    W003 = 'Wheel contains non-module at library toplevel'
    W004 = 'Module is not located at importable path'
    W005 = 'Wheel contains common toplevel directory in library'
    W006 = '__init__.py at top level of library'
    W007 = 'Wheel library is empty'
    W008 = 'Wheel is empty'
    W009 = 'Wheel contains multiple toplevel library entries'
    W010 = 'Toplevel library directory contains no Python modules'
    #W101 = 'Wheel library contains files not in source tree'
    #W102 = 'Wheel library is missing files in source tree'
    #W201 = 'Wheel library is missing specified toplevel entry'
    #W202 = 'Wheel library has undeclared toplevel entry'


@attr.s(auto_attribs=True)
class FailedCheck:
    check: Check
    args:  List[str] = attr.Factory(list)

    def show(self, filename: Optional[str] = None) -> str:
        s = ''
        if filename is not None:
            s = f'{filename}: '
        s += f'{self.check.name}: {self.check.value}'
        if self.args:
            s += ':'
            for a in self.args:
                s += f'\n  {a}'
        return s


def parse_checks_string(s: str) -> Set[Check]:
    """
    Convert a string of comma-separated check names & check name prefixes to a
    set of `Check`\\ s
    """
    checks = set()
    for cs in comma_split(s):
        new_checks = [chk for chk in Check if chk.name.startswith(cs)]
        if not new_checks:
            raise UserInputError(f'Unknown check prefix: {cs}')
        checks.update(new_checks)
    return checks
