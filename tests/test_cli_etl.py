"""
Unittests for gpsdio etl
"""


from click.testing import CliRunner

import gpsdio
import gpsdio.cli
import gpsdio.cli.main


# def test_sort_time(types_msg_gz_path, tmpdir, runner):
#
#     # Process everything and sort on timestamp
#     pth = str(tmpdir.mkdir('test').join('test_sort_time'))
#     result = runner.invoke(gpsdio.cli.main.main_group, [
#         'etl',
#         '--o-drv', 'MsgPack',
#         '--o-cmp', 'BZ2',
#         '--sort', 'timestamp',
#         types_msg_gz_path,
#         pth
#     ])
#
#     print(result.output)
#     assert result.exit_code is 0
#
#     prev = None
#     with gpsdio.open(pth, driver='MsgPack', compression='BZ2') as actual:
#         for msg in actual:
#             if prev is None:
#                 prev = msg
#             else:
#                 assert msg['timestamp'] >= prev['timestamp']


def test_sort_mmsi(types_msg_gz_path, tmpdir, runner):

    pth = str(tmpdir.mkdir('test').join('test_sort_mmsi'))
    result = runner.invoke(gpsdio.cli.main.main_group, [
        'etl',
        '--o-drv', 'MsgPack',
        '--o-cmp', 'BZ2',
        '--sort', 'mmsi',
        types_msg_gz_path,
        pth
    ])

    assert result.exit_code is 0

    prev = None
    with gpsdio.open(pth, driver='MsgPack', compression='BZ2') as actual:
        for msg in actual:
            if prev is None:
                prev = msg
            else:
                assert msg['mmsi'] >= prev['mmsi']


def test_filter(types_msg_gz_path, tmpdir, runner):

    pth = str(tmpdir.mkdir('test').join('test_filter'))
    result = runner.invoke(gpsdio.cli.main.main_group, [
        'etl',
        '--o-drv', 'MsgPack',
        '--o-cmp', 'BZ2',
        '--filter', "lat and lon",
        '--sort', 'lat',
        types_msg_gz_path,
        pth
    ])

    assert result.exit_code is 0

    prev = None
    with gpsdio.open(pth, driver='MsgPack', compression='BZ2') as actual:
        for msg in actual:
            if prev is None:
                prev = msg
            else:
                assert msg['lat'] >= prev['lat']
