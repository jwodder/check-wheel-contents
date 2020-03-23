import re
import attr
from   .errors import InvalidFilenameError

# These patterns are interpreted with re.UNICODE in effect, so there's probably
# some character that matches \d but not \w that needs to be included
PYTHON_TAG_RGX   = r'[\w\d]+'
ABI_TAG_RGX      = r'[\w\d]+'
PLATFORM_TAG_RGX = r'[\w\d]+'

WHEEL_FILENAME_CRGX = re.compile(
    r'(?P<project>[A-Za-z0-9](?:[A-Za-z0-9._]*[A-Za-z0-9])?)'
    r'-(?P<version>[A-Za-z0-9_.!+]+)'
    r'(?:-(?P<build>[0-9][\w\d.]*))?'
    r'-(?P<python_tags>{0}(?:\.{0})*)'
    ### XXX: distlib expects only one ABI tag in a filename.  Why?
    r'-(?P<abi_tags>{1}(?:\.{1})*)'
    r'-(?P<platform_tags>{2}(?:\.{2})*)'
    r'\.[Ww][Hh][Ll]'
    .format(PYTHON_TAG_RGX, ABI_TAG_RGX, PLATFORM_TAG_RGX)
)

@attr.s
class ParsedWheelFilename:
    #: The name of the project distributed by the wheel
    project       = attr.ib()
    #: The version of the project distributed by the wheel
    version       = attr.ib()
    #: The wheel's build tag (`None` if not defined)
    build         = attr.ib()
    #: A `list` of Python tags for the wheel
    python_tags   = attr.ib()
    #: A `list` of ABI tags for the wheel
    abi_tags      = attr.ib()
    #: A `list` of platform tags for the wheel
    platform_tags = attr.ib()

    def __str__(self):
        if self.build:
            fmt = '{0.project}-{0.version}-{0.build}-{1}-{2}-{3}.whl'
        else:
            fmt = '{0.project}-{0.version}-{1}-{2}-{3}.whl'
        return fmt.format(
            self,
            '.'.join(self.python_tags),
            '.'.join(self.abi_tags),
            '.'.join(self.platform_tags),
        )

    def tag_triples(self):
        """
        Returns a generator of all simple tag triples formed from the tags in
        the filename
        """
        for py in self.python_tags:
            for abi in self.abi_tags:
                for plat in self.platform_tags:
                    yield '-'.join([py, abi, plat])


def parse_wheel_filename(filename):
    """
    Parse a wheel filename into its components

    :param str filename: a wheel filename
    :rtype: ParsedWheelFilename
    :raises InvalidFilenameError: if the filename is invalid
    """
    m = WHEEL_FILENAME_CRGX.fullmatch(filename)
    if not m:
        raise InvalidFilenameError(filename)
    return ParsedWheelFilename(
        project       = m.group('project'),
        version       = m.group('version'),
        build         = m.group('build'),
        python_tags   = m.group('python_tags').split('.'),
        abi_tags      = m.group('abi_tags').split('.'),
        platform_tags = m.group('platform_tags').split('.'),
    )
