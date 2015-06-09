"""Unittests for `gpsdio.core`."""


import itertools
import tempfile
import unittest

import pytest
import six

from . import compare_msg
import gpsdio
import gpsdio.schema
import gpsdio.drivers
import gpsdio.pycompat
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

        with gpsdio.open(TYPES_MSG_FILE) as fp_msg, \
                gpsdio.open(TYPES_MSG_GZ_FILE) as fp_msg_gz, \
                gpsdio.open(TYPES_JSON_FILE) as fp_json, \
                gpsdio.open(TYPES_JSON_GZ_FILE) as fp_json_gz:

            for lines in zip(fp_msg, fp_msg_gz, fp_json, fp_json_gz):
                for pair in itertools.combinations(lines, 2):
                    self.assertTrue(compare_msg(*pair))

    def test_wrong_extension(self):

        with open(TYPES_MSG_FILE) as src:
            self.tempfile.write(src.read())
        self.tempfile.seek(0)

        with gpsdio.open(self.tempfile.name, driver='MsgPack') as actual, \
                gpsdio.open(TYPES_MSG_FILE) as expected:
            for e_line, a_line in zip(expected, actual):
                self.assertDictEqual(e_line, a_line)

        with tempfile.NamedTemporaryFile(mode='r+') as tfile:
            with open(TYPES_MSG_GZ_FILE) as src:
                tfile.write(src.read())
            tfile.seek(0)

            with gpsdio.open(tfile.name, driver='MsgPack', compression='GZIP') as actual, \
                    gpsdio.open(TYPES_MSG_GZ_FILE) as expected:
                for e_line, a_line in zip(expected, actual):
                    self.assertDictEqual(e_line, a_line)

    def test_no_detect_compression(self):

        with gpsdio.open(TYPES_MSG_FILE, compression=False) as actual, \
                gpsdio.open(TYPES_MSG_FILE) as expected:
            for e_line, a_line in zip(expected, actual):
                self.assertDictEqual(e_line, a_line)


class TestStream(unittest.TestCase):

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile(mode='r+')

    def tearDown(self):
        self.tempfile.close()

    def test_default_mode_is_read(self):
        with gpsdio.open(TYPES_MSG_FILE) as stream:
            self.assertEqual(stream.mode, 'r')

    def test_attrs(self):
        with gpsdio.open(TYPES_MSG_FILE) as stream:
            self.assertIsInstance(stream.__repr__(), six.string_types)
            self.assertTrue(hasattr(stream, '__next__'))

    def test_io_on_closed_stream(self):
        for mode in ('r', 'w', 'a'):
            with gpsdio.open(self.tempfile.name, mode=mode, driver='NewlineJSON') as stream:
                stream.close()
                self.assertTrue(stream.closed)
                with self.assertRaises(IOError):
                    next(stream)
                with self.assertRaises(IOError):
                    stream.write(None)
                with self.assertRaises(IOError):
                    stream.writeheader()

    def test_read_from_write_stream(self):
        with gpsdio.open(TYPES_MSG_GZ_FILE) as src, \
                gpsdio.open(self.tempfile.name, 'w', driver='NewlineJSON') as dst:
            for msg in src:
                dst.write(msg)
            with self.assertRaises(IOError):
                next(dst)

    def test_write_to_read_stream(self):
        with tempfile.NamedTemporaryFile(mode='r+') as f:
            for mode in ('r', 'a'):
                with gpsdio.open(f.name, mode=mode, driver='MsgPack') as src:
                    with self.assertRaises(IOError):
                        src.writeheader()


def test_get_driver():

    for d in [_d for _d in gpsdio.drivers.BaseDriver.by_name.values()]:
        rd = gpsdio.drivers.get_driver(d.driver_name)
        assert rd == d, "%r != %r" % (d, rd)
    try:
        gpsdio.drivers.get_driver('__---Invalid---__')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_get_compression():

    for c in [_d for _d in gpsdio.drivers.BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        cd = gpsdio.drivers.get_compression(c.name)
        assert cd == c, "%r != %r" % (c, cd)
    try:
        gpsdio.drivers.get_compression('__---Invalid---__')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_detect_file_type():

    for d in [_d for _d in gpsdio.drivers.BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        for ext in d.extensions:
            rd = gpsdio.drivers.detect_file_type('path.%s.ext' % ext)
            assert d == rd, "%r != %r" % (d, rd)
    try:
        gpsdio.drivers.detect_file_type('__---Invalid---__.ext.ext2')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_detect_compression_type():

    for c in [_d for _d in gpsdio.drivers.BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        print(c)
        print(c.extensions)
        for ext in c.extensions:
            cd = gpsdio.drivers.detect_compression_type(('path.something.%s' % ext))
            assert c == cd, "%r != %r" % (c, cd)
    try:
        gpsdio.drivers.get_compression('__---Invalid---__.ext.ext2')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_filter():

    # Pass all through unaltered
    with gpsdio.open(TYPES_MSG_GZ_FILE) as actual, gpsdio.open(TYPES_MSG_GZ_FILE) as expected:
        for a, e in zip(gpsdio.filter(actual, "isinstance(mmsi, int)"), expected):
            assert a == e

    # Extract only types 1, 2, and 3
    passed = []
    with gpsdio.open(TYPES_MSG_GZ_FILE) as stream:
        for msg in gpsdio.filter(stream, "type in (1,2,3)"):
            passed.append(msg)
            assert msg['type'] in (1, 2, 3)
    assert len(passed) >= 3

    # Filter out everything
    with gpsdio.open(TYPES_MSG_GZ_FILE) as stream:
        for msg in gpsdio.filter(stream, ("type is 5", "mmsi is -1000")):
            assert False, "Above loop should not have executed because the filter should " \
                          "not have yielded anything."

    # Multiple expressions
    passed = []
    with gpsdio.open(TYPES_MSG_GZ_FILE) as stream:
        for msg in gpsdio.filter(
                stream, ("status == 'Under way using engine'", "mmsi is 366268061")):
            passed.append(msg)
            assert msg['mmsi'] is 366268061

    # Reference the entire message
    passed = []
    with gpsdio.open(TYPES_JSON_GZ_FILE) as stream:
        for msg in gpsdio.filter(stream, ("isinstance(msg, dict)", "'lat' in msg")):
            passed.append(msg)
            assert 'lat' in msg
    assert len(passed) >= 9

    # Multiple complex filters
    criteria = ("turn is 0 and second is 0", "mmsi == 366268061", "'lat' in msg")
    with gpsdio.open(TYPES_JSON_GZ_FILE) as stream:
        passed = [m for m in gpsdio.filter(stream, criteria)]
        assert len(passed) >= 1


# class TestBaseDriver(unittest.TestCase):
#
#     def test_attrs(self):
#         self.assertTrue(hasattr(gpsdio.drivers.BaseDriver, '__next__'))
#
#     def test_driver_context_manager(self):
#         with tempfile.NamedTemporaryFile(mode='r') as tfile:
#             with gpsdio.drivers.NewlineJSON(tfile, mode='r'):
#                 pass
#
#     def test_invalid_mode(self):
#         with self.assertRaises(ValueError):
#             gpsdio.drivers.FileDriver(None, mode='invalid')
#
#     def test_instantiated_properties(self):
#         modes = ('r', 'w', 'a')
#         name = 'drivername'
#         bd = gpsdio.drivers.BaseDriver(None, mode='r', modes=modes, name=name, reader=lambda x: x)
#         self.assertEqual(bd.modes, modes)
#         self.assertEqual(bd.name, name)
