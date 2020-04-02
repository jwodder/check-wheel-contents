from   enum      import Enum
from   functools import reduce
from   operator  import or_
from   typing    import List, Optional, Set
import attr
from   .errors   import UserInputError
from   .util     import comma_split

class Check(Enum):
    """
    A enumeration of the various checks and their corresponding error messages
    """
    W001 = 'Wheel contains .pyc/.pyo files'
    W002 = 'Wheel contains duplicate files'
    W003 = 'Wheel contains non-module at library toplevel'
    W004 = 'Module is not located at importable path'
    W005 = 'Wheel contains common toplevel name in library'
    W006 = '__init__.py at top level of library'
    W007 = 'Wheel library is empty'
    W008 = 'Wheel is empty'
    W009 = 'Wheel contains multiple toplevel library entries'
    W010 = 'Toplevel library directory contains no Python modules'
    W101 = 'Wheel library is missing files in package tree'
    W102 = 'Wheel library contains files not in package tree'
    W201 = 'Wheel library is missing specified toplevel entry'
    W202 = 'Wheel library has undeclared toplevel entry'


@attr.s(auto_attribs=True)
class FailedCheck:
    """ A check that has failed """

    #: The check that failed
    check: Check
    #: The relevant filepaths, if any
    args:  List[str] = attr.Factory(list)

    def show(self, filename: Optional[str] = None) -> str:
        """
        Return a string showing the check name, error message, and file paths
        (if any).  If ``filename`` is specified, it is taken to be the name of
        the wheel that was being checked, and it is placed at the beginning of
        the string.
        """
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
    return parse_check_prefixes(comma_split(s))

def parse_check_prefixes(prefixes: List[str]) -> Set[Check]:
    """
    Convert a list of check names & check name prefixes to a set of `Check`\\ s
    """
    return reduce(or_, map(parse_check_prefix, prefixes), set())

def parse_check_prefix(s: str) -> Set[Check]:
    """
    Convert a check name or check name prefix to the set of `Check`\\ s that it
    represents
    """
    if not s:
        raise UserInputError(f'Unknown/invalid check prefix: {s!r}')
    checks = {c for c in Check if c.name.startswith(s)}
    if not checks:
        raise UserInputError(f'Unknown/invalid check prefix: {s!r}')
    return checks
