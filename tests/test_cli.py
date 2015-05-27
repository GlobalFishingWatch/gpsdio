"""
Unittests for `gpsdio.cli`
"""


import tempfile

from click.testing import CliRunner
import newlinejson as nlj

import gpsdio
import gpsdio.cli
import gpsdio.drivers
from sample_files import TYPES_MSG_GZ_FILE
from sample_files import TYPES_JSON_FILE


# Click's CliRunner() class crashes on this test because gpsdio is closing sys.stdout
# and CliRunner() expects to do that itself.  Not sure what the work-around is.
#
# def test_cat():
#     result = CliRunner().invoke(gpsdio.cli.main, [
#         'cat',
#         TYPES_MSG_GZ_FILE
#     ])
#     assert result.exit_code is 0
#     with gpsdio.open(TYPES_MSG_GZ_FILE) as expected:
#         for expected, actual in zip(expected, nlj.loads(result.output)):
#             assert expected == actual


def test_env():
    result = CliRunner().invoke(gpsdio.cli.main, [
        'env',
        '--drivers'
    ])
    assert result.exit_code is 0
    for name in gpsdio.drivers.BaseDriver.by_name.keys():
        assert name in result.output
    result = CliRunner().invoke(gpsdio.cli.main, [
        'env',
        '--compression'
    ])
    assert result.exit_code is 0
    for name in gpsdio.drivers.BaseCompressionDriver.by_name.keys():
        assert name in result.output


def test_load():

    with open(TYPES_JSON_FILE) as f, tempfile.NamedTemporaryFile('r+') as dst:
        stdin_input = f.read()
        print(stdin_input)

        result = CliRunner().invoke(gpsdio.cli.main, [
            '--output-driver', 'NewlineJSON',
            '--output-compression', 'GZIP',
            'load',
            dst.name

        ], input=stdin_input)

        dst.seek(0)
        print(result.exception)
        assert result.exit_code is 0

        with gpsdio.open(TYPES_MSG_GZ_FILE) as expected, \
                gpsdio.open(dst.name, driver='NewlineJSON', compression='GZIP') as actual:
            for e, a in zip(expected, actual):
                assert e == a
