

"""
Drivers for reading and writing a variety of formats and compression.
"""


import bz2
import logging
import gzip
import sys

import msgpack
import six

from gpsdio.base import BaseDriver as _BaseDriver
from gpsdio.base import BaseCompressionDriver as _BaseCompressionDriver


logger = logging.getLogger('gpsdio')


def get_driver(name):

    """
    Accepts a string and returns the driver class associated with that name.
    """

    if name in _BaseDriver.by_name:
        return _BaseDriver.by_name[name]
    else:
        raise ValueError("Unrecognized driver name: %s" % name)


def get_compression(name):

    """
    Accepts a string and returns the driver class associated with that name.
    """

    if name in _BaseCompressionDriver.by_name:
        return _BaseCompressionDriver.by_name[name]
    else:
        raise ValueError("Unrecognized compression name: %s" % name)


def detect_file_type(path):

    """
    Given an file path, attempt to determine appropriate driver.
    """

    for ext in path.split('.')[-2:]:
        if ext in _BaseDriver.by_extension:
            return _BaseDriver.by_extension[ext]
    else:
        raise ValueError("Can't determine driver: %s" % path)


class NewlineJSON(_BaseDriver):

    """
    Access data stored as newline delimited JSON.  Driver options are passed to
    ``newlinejson.open()``.

    https://github.com/geowurster/NewlineJSON
    """

    name = 'NewlineJSON'
    extensions = ('json', 'nljson')
    io_modes = ('r', 'w', 'a')

    def open(self, name, mode='r', **kwargs):
        import newlinejson as nlj
        return nlj.open(name, mode=mode, **kwargs)


class GZIP(_BaseCompressionDriver):

    """
    Access data stored as GZIP using Python's builtin ``gzip`` library.  Driver
    options are passed to ``gzip.open()``, unless the input path is a file-like
    object, in which case they are passed to ``gzip.GzipFile()``.
    Input file is automatically opened in ``rb`` mode when reading in Python3.
    https://docs.python.org/3/library/gzip.html
    """

    name = 'GZIP'
    extensions = 'gz',
    io_modes = ('r', 'w', 'a')

    def open(self, name, mode='r', **kwargs):

        if name == sys.stdin:
            raise IOError("GZIP can't read directly from stdin")
        elif isinstance(name, six.string_types):
            return gzip.open(name, mode=mode, **kwargs)
        else:
            return gzip.GzipFile(fileobj=name, mode=mode, **kwargs)

    def load(self, msg):
        if hasattr(msg, 'decode'):
            msg = msg.decode('utf-8')
        return msg

    def dump(self, msg):
        if six.PY3 and isinstance(msg, six.string_types):
            msg = bytes(msg, 'utf-8')
        return msg

    def read(self, *args, **kwargs):
        return self.f.read(*args, **kwargs)


class BZ2(_BaseCompressionDriver):

    """
    Access data stored as BZ2 with Python's builtin ``bz2`` library.  Driver
    options are passed to ``bz2.BZ2File()``.
    Files are automatically opened in ``rb`` mode when reading in Python3.
    https://docs.python.org/3/library/bz2.html
    """

    name = 'BZ2'
    extensions = 'bz2',
    io_modes = 'r', 'w', 'a'

    def open(self, name, mode='r', **kwargs):
        if mode == 'w':
            mode = 'wb'
        return bz2.BZ2File(name, mode=mode, **kwargs)

    def read(self, *args, **kwargs):
        return self.f.read(*args, **kwargs)

    def dump(self, msg):
        if not isinstance(msg, six.binary_type):
            msg.encode('utf-8')
        return msg


class NMEA(_BaseDriver):

    name = 'NMEA'
    extensions = 'nmea',
    io_modes = 'r',
    field_map = {
        'cog': 'course',
        'id': 'type',
        'nav_status': 'status',
        'position_accuracy': 'accuracy',
        'repeat_indicator': 'repeat',
        'rot': 'turn',
        'sog': 'speed',
        'special_manoeuvre': 'maneuver',
        'timestamp': 'second',
        'true_heading': 'heading',
        'imo_num': 'imo',
        'x': 'lon',
        'y': 'lat'
    }

    def open(self, name, mode='r', **kwargs):
        import ais
        return ais.open(name, mode=mode, **kwargs)

    def load(self, msg):
        msg = {self.field_map.get(k, k): v for k, v in six.iteritems(msg['decoded'])}
        msg = {
            fld: msg.get(fld, dfn.get('default'))
            for fld, dfn in self.schema[msg['type']].items()}

        # Adjust libais not-available values to match AIVDM
        if 'course' in msg and msg['course'] == 360:
            msg['course'] = self.schema[msg['type']]['course']['default']
        if 'second' in msg and msg['second'] > 60:
            msg['second'] = self.schema[msg['type']]['course']['default']
        if msg['type'] != 9 and 'speed' in msg and round(msg['speed'], 0) == 102:
            msg['speed'] = self.schema[msg['type']]['speed']['default']
        if 'maneuver' in msg and msg['maneuver'] == 3:
            msg['maneuver'] = self.schema[msg['type']]['maneuver']['default']
        if 'hour' in msg and msg['hour'] > 23:
            msg['hour'] = self.schema[msg['type']]['hour']['default']
        if 'seqno' in msg and msg['seqno'] is None:
            msg['seqno'] = self.schema[msg['type']]['seqno']['default']
        if 'heading' in msg and msg['heading'] > 359:
            msg['heading'] = self.schema[msg['type']]['heading']['default']

        # TODO: libais gives float for draught.  Should be int?

        # Return formatted message and strip whitespace from strings
        return {k: v.strip() if isinstance(v, six.string_types) else v
                for k, v in six.iteritems(msg)}


class MsgPack(_BaseDriver):

    """
    Read and write data stored as MsgPack.  When reading, driver options are
    passed to ``msgpack.Unpacker()`` and ``msgpack.Packer()`` when writing.
    If not specified, encoding will be set to ``utf-8`` to avoid receiving
    bytestrings.  In Python3 input files are automatically opened in ``rb`` if
    opening in ``r`` mode.  When passing in an already open file, the file must
    have been opened in ``rb`` mode.
    https://github.com/msgpack/msgpack-python
    """

    name = 'MsgPack'
    extensions = ('msg', 'msgpack')
    io_modes = ('r', 'w', 'a')

    def open(self, name, mode='r', **kwargs):

        if 'encoding' not in kwargs:
            kwargs['encoding'] = 'utf-8'

        # We need some additional MsgPack specific objects
        self._unpacker = None
        self._unpacker_args = kwargs
        self.packer = msgpack.Packer(**kwargs)

        if mode == 'r':
            mode = 'rb' if six.PY3 else 'r'
        elif mode == 'w':
            mode = 'w'

        if isinstance(name, six.string_types):
            return open(name, mode=mode)
        else:
            return name

    def __next__(self):
        if self._unpacker is None:
            self._unpacker = msgpack.Unpacker(self.f, **self._unpacker_args)
        return next(self._unpacker)

    next = __next__

    def dump(self, msg):
        return self.packer.pack(msg)


_DRIVERS = _BaseDriver.by_name
_DRIVERS_BY_EXT = _BaseDriver.by_extension
_COMPRESSION = _BaseCompressionDriver.by_name
_COMPRESSION_BY_EXT = _BaseCompressionDriver.by_extension
