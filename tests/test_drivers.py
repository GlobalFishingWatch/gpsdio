"""
Unittests for `gpsdio.drivers`.
"""


from __future__ import unicode_literals

import itertools
import tempfile

from . import compare_msg
from gpsdio import drivers
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

        stream = odrv.stream
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
