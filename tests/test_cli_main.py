"""
Unittests for gpsdio.cli.main
"""


from click.testing import CliRunner

import gpsdio
import gpsdio.cli


def test_version():
    result = CliRunner().invoke(gpsdio.cli.main.main_group, [
        '--version'
    ])
    print(result.output)
    assert result.exit_code is 0
    assert gpsdio.__version__ in result.output
