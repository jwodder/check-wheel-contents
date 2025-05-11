v0.6.2 (2025-05-11)
-------------------
- Update tests for click v8.2.0
- Drop support for Python 3.8 and 3.9

v0.6.1 (2024-12-01)
-------------------
- Migrated from setuptools to hatch
- Drop support for Python 3.7
- Support Python 3.13

v0.6.0 (2023-10-31)
-------------------
- Support Python 3.12
- Add type annotations to tests
- W005 will no longer fail for common names that are provided to `--toplevel`
  (contributed by [@gaborbernat](https://github.com/gaborbernat))

v0.5.0 (2023-09-23)
-------------------
- Update pydantic to v2.0

v0.4.0 (2022-10-25)
-------------------
- Drop support for Python 3.6
- Support Python 3.11
- Use `tomllib` on Python 3.11

v0.3.4 (2022-01-02)
-------------------
- Support Python 3.10
- Support tomli 2.0

v0.3.3 (2021-08-02)
-------------------
- Update for tomli 1.2.0

v0.3.2 (2021-07-08)
-------------------
- Replace `property-manager` with `functools.cached_property` (Python 3.8+) /
  `cached-property` (pre-Python 3.8)
- Open TOML files using UTF-8 (contributed by
  [@domdfcoding](https://github.com/domdfcoding))
- Get tests to pass on Windows

v0.3.1 (2021-07-02)
-------------------
- Switch from toml to tomli

v0.3.0 (2021-05-12)
-------------------
- Make sdists include `*.pyc` files from the test data directory
- Use [`pydantic`](https://github.com/samuelcolvin/pydantic) for configuration
  validation
- Add `app`, `cli`, `lib`, and `scripts` to the set of common toplevel names
  checked for by W005
- Support Click 8

v0.2.0 (2020-11-07)
-------------------
- Paths passed to `src_dir` in a configuration file are now required to be
  directories
- Support Python 3.9
- Support wheels whose filenames, `.dist-info` directories, and `.data`
  directories use different casings/spellings for the project name and/or
  version
- Drop `read_version` build dependency

v0.1.0 (2020-04-02)
-------------------
Initial release
