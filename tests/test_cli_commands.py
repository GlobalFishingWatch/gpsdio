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
#     result = CliRunner().invoke(gpsdio.cli.main_group, [
#         'cat',
#         TYPES_MSG_GZ_FILE
#     ])
#     assert result.exit_code is 0
#     with gpsdio.open(TYPES_MSG_GZ_FILE) as expected:
#         for expected, actual in zip(expected, nlj.loads(result.output)):
#             assert expected == actual


def test_env():
    result = CliRunner().invoke(gpsdio.cli.main_group, [
        'env',
        '--drivers'
    ])
    assert result.exit_code is 0
    for name in gpsdio.drivers.BaseDriver.by_name.keys():
        assert name in result.output
    result = CliRunner().invoke(gpsdio.cli.main_group, [
        'env',
        '--compression'
    ])
    assert result.exit_code is 0
    for name in gpsdio.drivers.BaseCompressionDriver.by_name.keys():
        assert name in result.output

    result = CliRunner().invoke(gpsdio.cli.main_group, [
        'env',
    ])
    assert result.exit_code is not 0


def test_load():

    with open(TYPES_JSON_FILE) as f, tempfile.NamedTemporaryFile('r+') as dst:
        stdin_input = f.read()
        print(stdin_input)

        result = CliRunner().invoke(gpsdio.cli.main_group, [
            '--o-drv', 'NewlineJSON',
            '--o-cmp', 'GZIP',
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


def test_etl():

    driver = 'MsgPack'
    comp = 'BZ2'

    # Process everything and sort on timestamp
    with tempfile.NamedTemporaryFile('r+') as f:
        result = CliRunner().invoke(gpsdio.cli.main_group, [
            '--o-drv', driver,
            '--o-cmp', comp,
            'etl',
            '--sort', 'timestamp',
            TYPES_MSG_GZ_FILE,
            f.name
        ])
        f.seek(0)

        assert result.exit_code is 0

        prev = None
        with gpsdio.open(f.name, driver=driver, compression=comp) as actual:
            for msg in actual:
                if prev is None:
                    prev = msg
                else:
                    assert msg['timestamp'] >= prev['timestamp']

    # Process everything and sort on mmsi
    with tempfile.NamedTemporaryFile('r+') as f:
        result = CliRunner().invoke(gpsdio.cli.main_group, [
            '--o-drv', driver,
            '--o-cmp', comp,
            'etl',
            '--sort', 'mmsi',
            TYPES_MSG_GZ_FILE,
            f.name
        ])
        f.seek(0)

        assert result.exit_code is 0

        prev = None
        with gpsdio.open(f.name, driver=driver, compression=comp) as actual:
            for msg in actual:
                if prev is None:
                    prev = msg
                else:
                    assert msg['mmsi'] >= prev['mmsi']

    # Filter and process
    with tempfile.NamedTemporaryFile('r+') as f:
        result = CliRunner().invoke(gpsdio.cli.main_group, [
            '--o-drv', driver,
            '--o-cmp', comp,
            'etl',
            '--filter', "lat and lon",
            '--sort', 'lat',
            TYPES_MSG_GZ_FILE,
            f.name
        ])
        f.seek(0)

        assert result.exit_code is 0

        prev = None
        with gpsdio.open(f.name, driver=driver, compression=comp) as actual:
            for msg in actual:
                if prev is None:
                    prev = msg
                else:
                    assert msg['lat'] >= prev['lat']
