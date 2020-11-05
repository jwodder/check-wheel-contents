from check_wheel_contents.checks import Check, FailedCheck

def test_show_no_args_no_filename():
    """
    Show the test file.

    Args:
    """
    fc = FailedCheck(Check.W001)
    assert fc.show() == f'W001: {Check.W001.value}'

def test_show_args_no_filename():
    """
    Show test test files.

    Args:
    """
    fc = FailedCheck(Check.W001, ['foo.pyc', 'bar/glarch.pyo'])
    assert fc.show() == (
        f'W001: {Check.W001.value}:\n'
        '  foo.pyc\n'
        '  bar/glarch.pyo'
    )

def test_show_args_filename():
    """
    Executes test.

    Args:
    """
    fc = FailedCheck(Check.W001, ['foo.pyc', 'bar/glarch.pyo'])
    assert fc.show('dist/foo-1.0-py3-none-any.whl') == (
        f'dist/foo-1.0-py3-none-any.whl: W001: {Check.W001.value}:\n'
        '  foo.pyc\n'
        '  bar/glarch.pyo'
    )

def test_show_no_args_filename():
    """
    Show test filename.

    Args:
    """
    fc = FailedCheck(Check.W001)
    assert fc.show('dist/foo-1.0-py3-none-any.whl') \
        == f'dist/foo-1.0-py3-none-any.whl: W001: {Check.W001.value}'
