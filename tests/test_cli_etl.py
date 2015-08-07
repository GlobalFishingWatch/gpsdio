"""
Unittests for gpsdio etl
"""


import tempfile

from click.testing import CliRunner

import gpsdio
import gpsdio.cli
from sample_files import TYPES_MSG_GZ_FILE


def test_sort_time():

    # Process everything and sort on timestamp
    with tempfile.NamedTemporaryFile('r+') as f:
        result = CliRunner().invoke(gpsdio.cli.main_group, [
            'etl',
            '--o-drv', 'MsgPack',
            '--o-cmp', 'BZ2',
            '--sort', 'timestamp',
            TYPES_MSG_GZ_FILE,
            f.name
        ])
        f.seek(0)

        assert result.exit_code is 0

        prev = None
        with gpsdio.open(f.name, driver='MsgPack', compression='BZ2') as actual:
            for msg in actual:
                if prev is None:
                    prev = msg
                else:
                    assert msg['timestamp'] >= prev['timestamp']

def test_sort_mmsi():

    # Process everything and sort on mmsi
    with tempfile.NamedTemporaryFile('r+') as f:
        result = CliRunner().invoke(gpsdio.cli.main_group, [
            'etl',
            '--o-drv', 'MsgPack',
            '--o-cmp', 'BZ2',
            '--sort', 'mmsi',
            TYPES_MSG_GZ_FILE,
            f.name
        ])
        f.seek(0)

        assert result.exit_code is 0

        prev = None
        with gpsdio.open(f.name, driver='MsgPack', compression='BZ2') as actual:
            for msg in actual:
                if prev is None:
                    prev = msg
                else:
                    assert msg['mmsi'] >= prev['mmsi']

def test_filter():

    # Filter and process
    with tempfile.NamedTemporaryFile('r+') as f:
        result = CliRunner().invoke(gpsdio.cli.main_group, [
            'etl',
            '--o-drv', 'MsgPack',
            '--o-cmp', 'BZ2',
            '--filter', "lat and lon",
            '--sort', 'lat',
            TYPES_MSG_GZ_FILE,
            f.name
        ])
        f.seek(0)

        assert result.exit_code is 0

        prev = None
        with gpsdio.open(f.name, driver='MsgPack', compression='BZ2') as actual:
            for msg in actual:
                if prev is None:
                    prev = msg
                else:
                    assert msg['lat'] >= prev['lat']
