"""
Unittests for `gpsdio.drivers`.
"""


import bz2
import itertools
import sys

import pytest

from gpsdio import drivers
import gpsdio.drivers


# def test_driver_read_matrix(
#         types_json_path, types_json_gz_path,types_msg_path, types_msg_gz_path, compare_msg):
#
#     open_drivers = [
#
#         drivers.NewlineJSON(types_json_path),
#         drivers.NewlineJSON(open(types_json_path)),
#
#         drivers.NewlineJSON(drivers.GZIP(types_json_gz_path)),
#         drivers.NewlineJSON(drivers.GZIP(open(types_json_gz_path))),
#
#         drivers.MsgPack(types_msg_path),
#         drivers.MsgPack(open(types_msg_path)),
#
#         drivers.MsgPack(drivers.GZIP(types_msg_gz_path)),
#         drivers.MsgPack(drivers.GZIP(open(types_msg_gz_path)))
#     ]
#
#     for lines in zip(*open_drivers):
#         for pair in itertools.combinations(lines, 2):
#             assert compare_msg(*pair)
#
#     for odrv in open_drivers:
#         odrv.close()
#
#         stream = odrv._stream
#         while stream:
#             assert stream.closed, stream
#             if hasattr(stream, '_f'):
#                 stream = stream._f
#             else:
#                 stream = None


# def test_msgpack(types_msg_path, compare_msg):
#
#     with tempfile.NamedTemporaryFile(mode='r+') as f:
#         with drivers.MsgPack(types_msg_path) as src, drivers.MsgPack(f.name, 'w') as dst:
#             for msg in src:
#                 dst.write(msg)
#         f.seek(0)
#         with drivers.MsgPack(types_msg_path) as expected, drivers.MsgPack(f.name) as actual:
#             for e, a in zip(expected, actual):
#                 assert compare_msg(e, a)
#
#     with tempfile.NamedTemporaryFile(mode='r+') as f:
#         with drivers.MsgPack(types_msg_path) as src, drivers.GZIP(f.name, 'w') as gzip:
#             with drivers.MsgPack(gzip, 'w') as dst:
#                 for msg in src:
#                     dst.write(msg)
#         with drivers.GZIP(f.name) as gzip:
#             with drivers.MsgPack(gzip) as actual, drivers.MsgPack(types_msg_path) as expected:
#                 for e, a in zip(expected, actual):
#                     assert compare_msg(e, a)


def test_get_compression():
    assert gpsdio.drivers.GZIP == gpsdio.drivers.get_compression('GZIP')
    with pytest.raises(ValueError):
        gpsdio.drivers.get_compression("bad-name")


def test_gzip_cannot_read_from_stdin():
    with pytest.raises(IOError):
        gpsdio.drivers.GZIP(sys.stdin)


def test_already_open_bzip2(types_json_bz2_path):
    with bz2.BZ2File(types_json_bz2_path) as f:
        with gpsdio.drivers.BZ2(f) as src:
            pass


def test_msg_bz2_round_robin(types_msg_bz2_path, tmpdir):
    pth = str(tmpdir.mkdir('test').join('test_bz2_round_robin.msg.bz2'))
    with gpsdio.open(types_msg_bz2_path) as src, gpsdio.open(pth, 'w') as dst:
        for msg in src:
            dst.write(msg)


def test_msg_gz_round_robin(types_msg_gz_path, tmpdir):
    pth = str(tmpdir.mkdir('test').join('test_gz_round_robin.msg.gz'))
    with gpsdio.open(types_msg_gz_path) as src, gpsdio.open(pth, 'w') as dst:
        for msg in src:
            dst.write(msg)
