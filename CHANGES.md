Changes
=======


0.0.7 (2015-07-30)
------------------

- Expose information about drivers through `gpsdio env --driver-help` - # 120
- `gpsdio insp` supports alternate interpreters and uses `src` var instead of `stream` - #109
- i/o drv/cmp options moved from main CLI to subcommands - #108
- Fixed a bug where `gpsdio.open('-', 'a')` would open `stdout` - #105
- Support for already open file pointers - #104
- Drivers must now implement an `open()` method - #99


0.0.6 (2015-06-25)
------------------

- `--indent 4` is now the default for `gpsdio info` but `--indent None` will disable indentation - #93
- Added `--with-field-hist` to `gpsdio info` to get a report message counts by field - #90
- External drivers must now subclass `gpsdio.base.Base/Compression/Driver` - #85
- IO mode is validated when opening a file based on the driver's `io_modes` - #75


0.0.5 (2015-06-24)
------------------

- Added `gpsdio info` CLI command - #86
- Fixed license typo in `setup.py` - # 82
- Require `six>=1.8` for metaclass support - #78


0.0.4 (2015-06-09)
------------------

- Support driver and compression options on the commandline and in `ctx.obj` - #71
- Added `[gpsdio.drivers]` entry-point to load external drivers - # 70
- Added `--quiet` and `--verbose` flags and stashed values in `ctx.obj` - #65, #67
- Added a `--version` flag - #66, #67
- `gpsdio validate` takes top-level arguments - #62


0.0.3 (2015-05-28)
------------------

- Critical packaging bug fix.


0.0.2 (2015-05-28)
------------------

- External CLI commands can now be registered via a `[gpsdio.gpsdio_plugins]` entry-point - #54
- `gpsdio.open()` can now read from `stdin` or write to `stdout` via '-' - #50
- Deprecated CLI command `gpsdio convert` in favor of `gpsdio etl` - #49
- New CLI commands: cat, env, etl, insp, and load - #49
- Better driver handling internally.


0.0.1 (2015-05-26)
------------------

- Rebranded `gpsd_format` as `gpsdio`.
- Initial development.
