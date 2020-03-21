import click
from   .checker  import WheelChecker
from   .contents import WheelContents
from   .util     import UserInputError

@click.command()
@click.option(
    '-c', '--config',
    type = click.Path(exists=True, dir_okay=False),
    help = 'Use the specified configuration file',
)
@click.argument('wheel', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.pass_context
def main(ctx, wheel, config, **kwargs):
    checker = WheelChecker()
    try:
        checker.read_config_file(config)
        checker.apply_command_options(**kwargs)
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
