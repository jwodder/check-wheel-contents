Golden Rules
============

1. No pull request will be accepted unless all of the tests pass

    - New contributors will have to wait for their PRs to be manually approved
      before GitHub Actions will test their contributions.  The wait should be
      no longer than 24 hours.

2. Lint your code!  Install [pre-commit](https://pre-commit.com) on your
   machine, run `pre-commit install` in your local clone of the repository, and
   then let pre-commit automatically format & lint the code before each commit.

3. If making a nontrivial contribution, add tests!  Tests are stored in
   `test/`, are written using [pytest](https://docs.pytest.org), and are run
   using [tox](http://tox.readthedocs.org).

4. Use type annotations in the main code!  Type checking is run via tox.

    - The tests do not need type annotations, but that's only because I didn't
      add any when I first wrote them, and adding annotations now would be a
      lot of work for very little payoff.

5. If adding or changing a feature, update the documentation in `README.rst`

6. If making a nontrivial contribution, add a summary to the "in development"
   section at the top of `CHANGELOG.md` (if there isn't one, start one);
   include your GitHub username and any issues that your PR closes.

    - I am aware that having everyone edit the same file could lead to merge
      conflicts, but until contributions become frequent enough that it's a
      recurring problem, manually editing `CHANGELOG.md` should be fine.  If
      it's not, we'll switch to towncrier or similar.


Adding a New Check
==================

Each new check needs an entry in the `Check` enum in `checks.py`, defining the
check's name and its error message, e.g.:

```python
class Check(Enum):
    ...
    W999 = "Wheel is square instead of round"
```

The actual implementation of a check is a `check_W999()` method on the
`WheelChecker` class in `checker.py`.  The method must take a `WheelContents`
(defined in `contents.py`) and return a list of `FailedCheck` instances.  A
`FailedCheck` combines a `Check` value and a list of filepaths (as strings)
that failed the check.  (For checks that do not involve filepaths, such as a
wheel being empty, omit the list of files.)

Generally, a check method should return at most one `FailedCheck` containing
all of the failing filepaths; only return multiple `FailedCheck`s if the check
applies to groups of files.  For example, W002 ("Wheel contains duplicate
files") returns a separate `FailedCheck` for each group of equal files.

Finally, write tests for your new check!  Check tests are in
`test/test_checking.py`.  A typical test for a check that only examines
filepaths in a wheel looks like this:

```python
@pytest.mark.parametrize(
    "paths,failures",
    [
        (
            [ ... list of paths in a wheel ... ],
            [ ... list of FailedChecks the check should return for the wheel ... ]
        ),
        (
            [ ... another list of paths ... ],
            [ ... another set of FailedChecks ... ],
        ),
        # etc.
    ],
)
def test_check_W999(paths, failures):
    checker = WheelChecker()
    assert checker.check_W999(wheel_from_paths(paths)) == failures
```

Be sure to test not only cases where the check fails but also ones where it
passes.  Try to aim for getting the coverage report shown at the end of a
successful test run to indicate that your entire check method is covered.


Adding a New Configuration Option
=================================

Adding a new configuration option involves updating the following locations:

- `__main__.py`: Add a new `@click.option`, add the parameter to `main()`, and
  pass the parameter to `checker.configure_options()`

- `config.py`:
    - Add the option as an attribute on `Configuration`.  For nontrivial types,
      a [pydantic](http://pydantic-docs.helpmanual.io) pre-validator should be
      added that parses string values from `.cfg`/`.ini` files (and, if
      necessary, structures found on the command line or in `pyproject.toml`)
      into a form that pydantic can convert into the attribute's final value.
    - Add the option as a parameter to `Configuration.from_command_options()`

- `checker.py`:
    - Add a parameter to `WheelChecker.configure_options()`
    - Add the final value for the option or what it represents as an attribute
      on `WheelChecker`, and populate the attribute in
      `WheelChecker.apply_config()`

- Tests:
    - Update the test cases for `test/test_main:test_options2configargs()` to
      handle the new command-line option

    - Test the new `Configuration` attribute by updating and adding new test
      cases to `test_from_command_options()` and updating
      `test_from_command_options_default()` in `test/test_configuration`

    - Add new test cases to `test/test_checker:test_configure_options()` to
      test the new `WheelChecker.configure_options()` parameter

    - Update `test_defaults()` and `test_apply_config_calls()` in
      `test/test_checker.py` for the new `WheelChecker` attribute
