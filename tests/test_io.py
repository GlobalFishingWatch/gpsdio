"""
Unittests for gpsdio.io
"""


import itertools
import json

import pytest
from six.moves import StringIO

import gpsdio
import gpsdio.schema
import gpsdio.drivers


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


def test_write_bad_msg(tmpdir):
    pth = str(tmpdir.mkdir('test').join('test_write_bad_msg'))
    with gpsdio.open(pth, 'w', driver='NewlineJSON') as dst:
        with pytest.raises(Exception):
            dst.write({'field': six})


def test_no_validate_messages():
    message = {'field': 'val'}
    stream = StringIO(json.dumps(message))
    with gpsdio.open(stream, driver='NewlineJSON', compression=False, _check=False) as src:
        msgs = list(src)
        assert len(msgs) is 1
        assert msgs[0] == message


def test_bad_message():
    message = {'mmsi': 123456789, 'type': 1}
    stream = StringIO(json.dumps(message))
    with pytest.raises(ValueError):
        with gpsdio.open(stream, driver='NewlineJSON', compression=False) as src:
            print(next(src))


def test_stream_attrs(types_json_path):

    # Valid path
    with gpsdio.open(types_json_path) as src:
        assert src.name == types_json_path

    # Stream with no name
    with gpsdio.open(StringIO(), driver='NewlineJSON', compression=False) as src:
        assert src.name == "<unknown name>"

    # I/O mode
    for m in ('r', 'w', 'a'):
        with gpsdio.open(StringIO(), mode=m, driver='NewlineJSON', compression=False) as src:
            assert src.mode == m

    # Schema structure
    with gpsdio.open(types_json_path) as src:
        # Stream is a driver that should also have the schema attached
        assert src._stream.schema == gpsdio.schema.build_schema()

    # Stop method, which is really just included because there's a start(),
    # so there should be a stop()
    with gpsdio.drivers.NewlineJSON() as drv:
        drv.start(types_json_path)
        assert not drv.closed
        assert not drv.f.closed
        drv.stop()
        assert drv.closed
        assert drv.f.closed
