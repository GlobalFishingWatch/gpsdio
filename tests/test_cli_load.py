"""
Unittests for gpsdio load
"""


import tempfile

from click.testing import CliRunner

import gpsdio
import gpsdio.cli
from sample_files import TYPES_JSON_FILE
from sample_files import TYPES_MSG_GZ_FILE



def test_load():

    with open(TYPES_JSON_FILE) as f, tempfile.NamedTemporaryFile('r+') as dst:
        stdin_input = f.read()
        print(stdin_input)

        result = CliRunner().invoke(gpsdio.cli.main_group, [
            'load',
            '--o-drv', 'NewlineJSON',
            '--o-cmp', 'GZIP',
            dst.name

        ], input=stdin_input)

        dst.seek(0)
        print(result.exception)
        assert result.exit_code is 0

        with gpsdio.open(TYPES_MSG_GZ_FILE) as expected, \
                gpsdio.open(dst.name, driver='NewlineJSON', compression='GZIP') as actual:
            for e, a in zip(expected, actual):
                assert e == a
