"""
Unittests for gpsd_format._io
"""

import os
import itertools
import json
import tempfile
import unittest
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from . import compare_msg
import gpsd_format
import gpsd_format.schema
import gpsd_format.drivers
import gpsd_format.pycompat
from .sample_files import *


VALID_ROWS = [
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 1},
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 2},
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 3},
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 4}
]

INVALID_ROWS = [
    {'type': 1, 'timestamp': 'morning'},
    {'type': 1, 'timestamp': 'late'}
]


class TestOpen(unittest.TestCase):

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile(mode='r+')

    def tearDown(self):
        self.tempfile.close()

    def test_standard(self):

        with gpsd_format.open(TYPES_MSG_FILE) as fp_msg, \
                gpsd_format.open(TYPES_MSG_GZ_FILE) as fp_msg_gz, \
                gpsd_format.open(TYPES_JSON_FILE) as fp_json, \
                gpsd_format.open(TYPES_JSON_GZ_FILE) as fp_json_gz:

            for lines in zip(fp_msg, fp_msg_gz, fp_json, fp_json_gz):
                for pair in itertools.combinations(lines, 2):
                    self.assertTrue(compare_msg(*pair))

    def test_wrong_extension(self):

        with open(TYPES_MSG_FILE) as src:
            self.tempfile.write(src.read())
        self.tempfile.seek(0)

        with gpsd_format.open(self.tempfile.name, driver='msgpack') as actual, \
                gpsd_format.open(TYPES_MSG_FILE) as expected:
            for e_line, a_line in zip(expected, actual):
                self.assertDictEqual(e_line, a_line)

        with tempfile.NamedTemporaryFile(mode='r+') as tfile:
            with open(TYPES_MSG_GZ_FILE) as src:
                tfile.write(src.read())
            tfile.seek(0)

            with gpsd_format.open(tfile.name, driver='msgpack', compression='gzip') as actual, \
                    gpsd_format.open(TYPES_MSG_GZ_FILE) as expected:
                for e_line, a_line in zip(expected, actual):
                    self.assertDictEqual(e_line, a_line)

    def test_no_detect_compression(self):

        with gpsd_format.open(TYPES_MSG_FILE, compression=False) as actual, \
                gpsd_format.open(TYPES_MSG_FILE) as expected:
            for e_line, a_line in zip(expected, actual):
                self.assertDictEqual(e_line, a_line)


class TestStream(unittest.TestCase):

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile(mode='r+')

    def tearDown(self):
        self.tempfile.close()

    def test_default_mode_is_read(self):
        with gpsd_format.open(TYPES_MSG_FILE) as stream:
            self.assertEqual(stream.mode, 'r')

    def test_attrs(self):
        with gpsd_format.open(TYPES_MSG_FILE) as stream:
            self.assertIsInstance(stream.__repr__(), gpsd_format.pycompat.string_types)
            self.assertTrue(hasattr(stream, '__next__'))

    def test_io_on_closed_stream(self):
        for mode in ('r', 'w', 'a'):
            with gpsd_format.open(self.tempfile.name, mode=mode, driver='newlinejson') as stream:
                stream.close()
                self.assertTrue(stream.closed)
                with self.assertRaises(IOError):
                    next(stream)
                with self.assertRaises(IOError):
                    stream.write(None)
                with self.assertRaises(IOError):
                    stream.writeheader()

    def test_read_from_write_stream(self):
        with gpsd_format.open(TYPES_MSG_GZ_FILE) as src, \
                gpsd_format.open(self.tempfile.name, 'w', driver='newlinejson') as dst:
            for msg in src:
                dst.write(msg)
            with self.assertRaises(IOError):
                next(dst)

    def test_write_to_read_stream(self):
        with tempfile.NamedTemporaryFile(mode='r+') as f:
            for mode in ('r', 'a'):
                with gpsd_format.open(f.name, mode=mode, driver='msgpack') as src:
                    with self.assertRaises(IOError):
                        src.writeheader()


def test_get_driver():

    for d in [_d for _d in gpsd_format.drivers.BaseDriver.by_name.values() if not _d.compression]:
        rd = gpsd_format.drivers.get_driver(d.name)
        assert rd == d, "%r != %r" % (d, rd)
    try:
        gpsd_format.drivers.get_driver('__---Invalid---__')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_get_compression():

    for c in [_d for _d in gpsd_format.drivers.BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        cd = gpsd_format.drivers.get_compression(c.name)
        assert cd == c, "%r != %r" % (c, cd)
    try:
        gpsd_format.drivers.get_compression('__---Invalid---__')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_detect_file_type():

    for d in [_d for _d in gpsd_format.drivers.BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        for ext in d.extensions:
            rd = gpsd_format.drivers.detect_file_type('path.%s.ext' % ext)
            assert d == rd, "%r != %r" % (d, rd)
    try:
        gpsd_format.drivers.detect_file_type('__---Invalid---__.ext.ext2')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_detect_compression_type():

    for c in [_d for _d in gpsd_format.drivers.BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        print(c)
        print(c.extensions)
        for ext in c.extensions:
            cd = gpsd_format.drivers.detect_compression_type(('path.something.%s' % ext))
            assert c == cd, "%r != %r" % (c, cd)
    try:
        gpsd_format.drivers.get_compression('__---Invalid---__.ext.ext2')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


class TestBaseDriver(unittest.TestCase):

    def test_attrs(self):
        self.assertTrue(hasattr(gpsd_format.drivers.BaseDriver, '__next__'))

    def test_driver_context_manager(self):
        with tempfile.NamedTemporaryFile(mode='r') as tfile:
            with gpsd_format.drivers.BaseDriver(tfile, mode='r', reader=lambda x: x, writer=None):
                pass

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            gpsd_format.drivers.BaseDriver(None, mode='invalid')

    def test_instantiated_properties(self):
        modes = ('r', 'w', 'a')
        name = 'drivername'
        bd = gpsd_format.drivers.BaseDriver(None, mode='r', modes=modes, name=name, reader=lambda x: x)
        self.assertEqual(bd.modes, modes)
        self.assertEqual(bd.name, name)
