import click
from   .checker  import WheelChecker
from   .contents import WheelContents

@click.command()
@click.argument('wheel', nargs=-1)
def main(wheel, **kwargs):
    checker = WheelChecker()
    try:
        checker.apply_config_dict(???)
        checker.apply_command_options(**kwargs)
    except UserInputError:
        ???
    ok = True
    for w in wheel:
        contents = WheelContent.from_wheel(w)
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
