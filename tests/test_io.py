"""
Unittests for gpsdio.io
"""


import itertools
import gzip

import newlinejson as nlj
import pytest
import six

import gpsdio
import gpsdio.schema
import gpsdio.drivers


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


def test_standard(
        types_msg_path, types_msg_gz_path, types_json_path, types_json_gz_path, compare_msg):

    with gpsdio.open(types_msg_path) as fp_msg, \
            gpsdio.open(types_msg_gz_path) as fp_msg_gz, \
            gpsdio.open(types_json_path) as fp_json, \
            gpsdio.open(types_json_gz_path) as fp_json_gz:

        for lines in zip(fp_msg, fp_msg_gz, fp_json, fp_json_gz):
            for pair in itertools.combinations(lines, 2):
                assert compare_msg(*pair)


def test_no_detect_compression(types_msg_path):

    with gpsdio.open(types_msg_path, compression=False) as actual, \
            gpsdio.open(types_msg_path) as expected:
        for e_line, a_line in zip(expected, actual):
            assert e_line == a_line


def test_default_mode_is_read(types_msg_path):
    with gpsdio.open(types_msg_path) as stream:
        assert stream.mode == 'r'


def test_attrs(types_msg_path):
    with gpsdio.open(types_msg_path) as stream:
        assert isinstance(stream.__repr__(), six.string_types)
        assert hasattr(stream, '__next__')


def test_io_on_closed_stream(tmpdir):

    # Make sure the tempfile actually appears on disk
    pth = str(tmpdir.mkdir('test').join('test_io_on_closed_file'))
    with open(pth, 'w') as f:
        f.write('')

    # Have to check in read and write in order to trigger all the exceptions
    for mode in ('r', 'w'):
        with gpsdio.open(pth, mode=mode, driver='NewlineJSON') as src:
            src.close()
        assert src.closed
        with pytest.raises((IOError, TypeError)):
            next(src)
        with pytest.raises((IOError, OSError, AttributeError)):
            src.write(None)


def test_read_from_write_stream(types_msg_gz_path, tmpdir):
    pth = str(tmpdir.mkdir('test').join('rw-io.json'))
    with gpsdio.open(types_msg_gz_path) as src, \
            gpsdio.open(pth, 'w', driver='NewlineJSON') as dst:
        for msg in src:
            dst.write(msg)
        with pytest.raises(TypeError):
            next(dst)


def test_get_driver():

    for d in [_d for _d in gpsdio.drivers._BaseDriver.by_name.values()]:
        rd = gpsdio.drivers.get_driver(d.name)
        assert rd == d, "%r != %r" % (d, rd)
    try:
        gpsdio.drivers.get_driver('__---Invalid---__')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_get_compression():

    for c in [_d for _d in gpsdio.drivers._BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        cd = gpsdio.drivers.get_compression(c.name)
        assert cd == c, "%r != %r" % (c, cd)
    try:
        gpsdio.drivers.get_compression('__---Invalid---__')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_detect_file_type():

    for d in [_d for _d in gpsdio.drivers._BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        for ext in d.extensions:
            rd = gpsdio.drivers.detect_file_type('path.%s.ext' % ext)
            assert d == rd, "%r != %r" % (d, rd)
    try:
        gpsdio.drivers.detect_file_type('__---Invalid---__.ext.ext2')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_detect_compression_type():

    for c in [_d for _d in gpsdio.drivers._BaseDriver.by_name if getattr(_d, 'compresion', False)]:
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


def test_write_bad_msg(tmpdir):
    pth = str(tmpdir.mkdir('test').join('test_write_bad_msg'))
    with gpsdio.open(pth, 'w', driver='NewlineJSON') as dst:
        with pytest.raises(Exception):
            dst.write({'field': six})
