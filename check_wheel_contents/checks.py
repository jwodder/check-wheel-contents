from   enum import Enum
import attr

class Check(Enum):
    W001 = 'Wheel contains .pyc/.pyo files'
    W002 = 'Wheel contains duplicate files'
    W003 = 'Wheel contains non-module at library toplevel'
    W004 = 'Module is not located at importable path'
    W005 = 'Wheel contains common toplevel directory in library'
        ### TODO: Rethink W005's message
    W006 = '__init__.py at top level of library'
    W007 = 'Wheel library is empty'
    W008 = 'Wheel contains multiple toplevel files'
    W009 = 'Toplevel library directory contains no .py files'
    W101 = 'Wheel contains files not in source tree'
    W102 = 'Wheel is missing files in source tree'
    W201 = 'Wheel is missing specifies toplevel entry'
    W202 = 'Wheel has undeclared toplevel entry'


@attr.s
class FailedCheck:
    check = attr.ib()
    args  = attr.ib()

    def show(self, filename=None):
        s = ''
        if filename is not None:
            s = f'{filename}: '
        s += f'{self.check.name}: {self.check.value}'
        if self.args:
            s += ':'
            for a in self.args:
                s += f'\n  {a}'
        return s
