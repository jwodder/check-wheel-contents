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
