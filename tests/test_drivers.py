"""
Unittests for `gpsdio.drivers`.
"""


import bz2
import itertools
import tempfile
import sys

import pytest

from . import compare_msg
from gpsdio import drivers
import gpsdio.drivers
from .sample_files import *


def test_driver_read_matrix():

    open_drivers = [

        drivers.NewlineJSON(TYPES_JSON_FILE),
        drivers.NewlineJSON(open(TYPES_JSON_FILE)),

        drivers.NewlineJSON(drivers.GZIP(TYPES_JSON_GZ_FILE)),
        drivers.NewlineJSON(drivers.GZIP(open(TYPES_JSON_GZ_FILE))),

        drivers.MsgPack(TYPES_MSG_FILE),
        drivers.MsgPack(open(TYPES_MSG_FILE)),

        drivers.MsgPack(drivers.GZIP(TYPES_MSG_GZ_FILE)),
        drivers.MsgPack(drivers.GZIP(open(TYPES_MSG_GZ_FILE)))
    ]

    for lines in zip(*open_drivers):
        for pair in itertools.combinations(lines, 2):
            assert compare_msg(*pair)

    for odrv in open_drivers:
        odrv.close()

        stream = odrv._stream
        while stream:
            assert stream.closed, stream
            if hasattr(stream, '_f'):
                stream = stream._f
            else:
                stream = None


def test_msgpack():

    with tempfile.NamedTemporaryFile(mode='r+') as f:
        with drivers.MsgPack(TYPES_MSG_FILE) as src, drivers.MsgPack(f.name, 'w') as dst:
            for msg in src:
                dst.write(msg)
        f.seek(0)
        with drivers.MsgPack(TYPES_MSG_FILE) as expected, drivers.MsgPack(f.name) as actual:
            for e, a in zip(expected, actual):
                assert compare_msg(e, a)

    with tempfile.NamedTemporaryFile(mode='r+') as f:
        with drivers.MsgPack(TYPES_MSG_FILE) as src, drivers.GZIP(f.name, 'w') as gzip:
            with drivers.MsgPack(gzip, 'w') as dst:
                for msg in src:
                    dst.write(msg)
        with drivers.GZIP(f.name) as gzip:
            with drivers.MsgPack(gzip) as actual, drivers.MsgPack(TYPES_MSG_FILE) as expected:
                for e, a in zip(expected, actual):
                    assert compare_msg(e, a)


def test_get_compression():
    assert gpsdio.drivers.GZIP == gpsdio.drivers.get_compression('GZIP')
    with pytest.raises(ValueError):
        gpsdio.drivers.get_compression("bad-name")


def test_gzip_cannot_read_from_stdin():
    with pytest.raises(IOError):
        gpsdio.drivers.GZIP(sys.stdin)


def test_already_open_bzip2():
    with bz2.BZ2File('sample-data/types.json.bz2') as f:
        with gpsdio.drivers.BZ2(f) as src:
            pass
