import click
from   .         import __version__
from   .checker  import WheelChecker
from   .checks   import parse_checks_string
from   .contents import WheelContents
from   .util     import UserInputError

class ChecksParamType(click.ParamType):
    name = 'checks'

    def convert(self, value, param, ctx):
        try:
            return parse_checks_string(value)
        except UserInputError as e:
            self.fail(str(e), param, ctx)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    __version__,
    '-V', '--version',
    message = '%(prog)s %(version)s',
)
@click.option(
    '-c', '--config',
    type = click.Path(exists=True, dir_okay=False),
    help = 'Use the specified configuration file',
)
@click.option(
    '--ignore',
    type    = ChecksParamType(),
    help    = 'Comma-separated list of checks to disable',
    metavar = 'CHECKS',
)
@click.option(
    '--select',
    type    = ChecksParamType(),
    help    = 'Comma-separated list of checks to enable',
    metavar = 'CHECKS',
)
@click.argument('wheel', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.pass_context
def main(ctx, wheel, config, select, ignore):
    checker = WheelChecker()
    try:
        checker.read_config_file(config)
        checker.load_command_options(select=select, ignore=ignore)
        checker.finalize_options()
    except UserInputError as e:
        ctx.fail(str(e))
    ok = True
    for w in wheel:
        contents = WheelContents.from_wheel(w)
        failures = checker.check_contents(contents)
        if failures:
            for f in failures:
                print(f.show(w))
            ok = False
        else:
            print(f'{w}: OK')
    ctx.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
