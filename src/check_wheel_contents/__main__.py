from   pathlib        import Path
from   typing         import Any, Iterable, List, Optional, Set, Tuple
import click
from   wheel_filename import InvalidFilenameError
from   .              import __version__
from   .checker       import NO_CONFIG, WheelChecker
from   .checks        import Check, parse_checks_string
from   .contents      import WheelContents
from   .errors        import UserInputError, WheelValidationError
from   .util          import comma_split

class ChecksParamType(click.ParamType):
    name = 'checks'

    def convert(
        self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Set[Check]:
        try:
            return parse_checks_string(value)
        except UserInputError as e:
            self.fail(str(e), param, ctx)


class ConfigParamType(click.ParamType):
    """
    Like ``click.Path(exists=True, dir_okay=False)``, except that `NO_CONFIG`
    is also allowed as a value
    """

    name = 'config'

    def convert(
        self,
        value: Any,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Any:
        if value is NO_CONFIG:
            return value
        else:
            return click.Path(exists=True, dir_okay=False)\
                        .convert(value, param, ctx)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    __version__,
    '-V', '--version',
    message = '%(prog)s %(version)s',
)
@click.option(
    '-c', '--config',
    type = ConfigParamType(),
    help = 'Use the specified configuration file',
)
@click.option(
    '--no-config',
    'config',
    flag_value = NO_CONFIG,
    help       = 'Do not read from a configuration file',
)
@click.option(
    '--ignore',
    type    = ChecksParamType(),
    help    = 'Comma-separated list of checks to disable',
    metavar = 'CHECKS',
)
@click.option(
    '--package',
    type     = click.Path(exists=True),
    multiple = True,
    help     = 'Module or package to expect in wheel library'
)
@click.option(
    '--package-omit',
    type    = comma_split,
    help    = 'Patterns in --package/--src-dir to ignore',
    metavar = 'PATTERNS',
)
@click.option(
    '--select',
    type    = ChecksParamType(),
    help    = 'Comma-separated list of checks to enable',
    metavar = 'CHECKS',
)
@click.option(
    '--src-dir',
    type     = click.Path(exists=True, file_okay=False),
    multiple = True,
    help     = 'Directory to expect contents of in wheel library'
)
@click.option(
    '--toplevel',
    type    = comma_split,
    help    = 'Comma-separated list of expected toplevel library entries',
    metavar = 'NAMES',
)
@click.argument('wheel', nargs=-1, type=click.Path(exists=True, dir_okay=True))
@click.pass_context
def main(
    ctx: click.Context,
    wheel: List[str],
    config: Any,
    select: Optional[Set[Check]],
    ignore: Optional[Set[Check]],
    toplevel: Optional[List[str]],
    package: Tuple[str, ...],
    src_dir: Tuple[str, ...],
    package_omit: Optional[List[str]],
) -> None:
    """
    Check that your wheels have the right contents.

    Visit <https://github.com/jwodder/check-wheel-contents> for more
    information.
    """
    checker = WheelChecker()
    try:
        checker.configure_options(
            configpath   = config,
            select       = select,
            ignore       = ignore,
            toplevel     = toplevel,
            package      = package,
            src_dir      = src_dir,
            package_omit = package_omit,
        )
    except UserInputError as e:
        ctx.fail(str(e))
    ok = True
    for w in args2wheelpaths(wheel):
        try:
            contents = WheelContents.from_wheel(w)
        except InvalidFilenameError:
            click.echo(f'{w}: wheel has invalid filename', err=True)
            ok = False
            continue
        except WheelValidationError as e:
            click.echo(f'{w}: invalid wheel: {e}', err=True)
            ok = False
            continue
        failures = checker.check_contents(contents)
        if failures:
            for f in failures:
                print(f.show(str(w)))
            ok = False
        else:
            print(f'{w}: OK')
    ctx.exit(0 if ok else 1)

def args2wheelpaths(args: List[str]) -> Iterable[Path]:
    """
    Convert a list of paths to `Path` objects and, if a given path is a
    directory, replace it with `Path`\\s to all wheels underneath it
    """
    for a in args:
        p = Path(a)
        if p.is_dir():
            yield from p.glob('**/*.[Ww][Hh][Ll]')
        else:
            yield p

if __name__ == '__main__':
    main()  # pragma: no cover
