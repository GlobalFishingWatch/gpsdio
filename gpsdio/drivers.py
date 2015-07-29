#!/usr/bin/env python

"""
Drivers for reading and writing a variety of formats and compression.
"""


import bz2
from codecs import open as codecs_open
import gzip
import logging
from pkg_resources import iter_entry_points

import msgpack
import newlinejson
import six
import ujson

from .base import BaseCompressionDriver as _BaseCompressionDriver
from .base import BaseDriver as _BaseDriver


newlinejson.JSON = ujson


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


def detect_compression_type(path):

    """
    Given a file path, attempt to determine the appropriate compression driver.
    """

    ext = path.rpartition('.')[-1]
    if ext in _BaseCompressionDriver.by_extension:
        return _BaseCompressionDriver.by_extension[ext]
    else:
        raise ValueError("Can't determine compression: %s" % path)


class NewlineJSON(_BaseDriver):

    """
    Driver for accessing data stored as newline delimited JSON.
    """

    driver_name = 'NewlineJSON'
    extensions = ('json', 'nljson')

    def open(self, f, mode='r', **kwargs):
        return newlinejson.open(f, mode=mode, **kwargs)


class MsgPack(_BaseDriver):

    """
    Driver for accessing data stored as MsgPack.
    """

    driver_name = 'MsgPack'
    extensions = ('msg', 'msgpack')

    class _MsgPackWriter(object):

        """
        A helper class to give this driver a `write()` method.  MsgPack doesn't
        offer a file-like object for writing and expects the user to do this:

            >>> import msgpack
            >>> packer = msgpack.Packer()
            >>> with open('out.msg', 'w') as f:
            ...     f.write(packer.pack({'key': 'val'}))

        which doesn't fit into the `gpsdio` driver model.
        """

        def __init__(self, f, **kwargs):

            """
            Store the properties required to make this thing work.

            Parameters
            ----------
            f : file
                A file-like object open for writing.
            kwargs : **kwargs, optional
                Additional keyword arguments for `msgpack.Packer()`.
            """

            self._packer = msgpack.Packer(**kwargs)
            self._f = f

        def write(self, msg):

            """
            Pack and write data to the underlying file-like object.
            """

            self._f.write(self._packer.pack(msg))

        def __getattr__(self, item):

            """
            For all other methods default to the underlying file-like object.
            """

            return getattr(self._f, item)

    class _MsgPackReader(msgpack.Unpacker):

        """
        A helper class to make `msgpack.Unpacker()` behave similarly to `file`.
        """

        def __init__(self, f, **kwargs):

            """
            Instantiate `msgpack.Unpacker()` from an open file-like object.

            Parameters
            ----------
            f : file
                A file-like object open for reading.
            kwargs : **kwargs, optional
                Additional keyword arguments for `msgpack.Unpacker()`.
            """

            self._f = f
            msgpack.Unpacker.__init__(self, f, **kwargs)

        def __getattr__(self, item):

            """
            For all other methods default to the underlying file-like object.
            """

            return getattr(self._f, item)

    def open(self, f, mode='r', **kwargs):

        """
        Constructs the necessary objects for reading or writing and hands them
        off to `BaseDriver()`.  When reading `msgpack.Unpacker()` is used but
        when writing a special helper `_MsgPackWriter()` is used.

        Parameters
        ----------
        f : str or file
            Input file path or open file-like object.
        mode : str, optional
            Mode to open `f` with.
        kwargs : **kwargs, optional
            Additional keyword arguments for `msgpack.Unpacker()` or
            `msgpack.Unpacker()`.
        """

        if isinstance(f, six.string_types):
            _f = codecs_open(f, mode=mode)
        else:
            _f = f
        if mode == 'r':
            return self._MsgPackReader(_f, **kwargs)
        else:
            return self._MsgPackWriter(_f, **kwargs)


class GZIP(_BaseCompressionDriver):

    """
    Driver for accessing data stored as GZIP.
    """

    driver_name = 'GZIP'
    extensions = 'gz',

    def open(self, f, mode='r', **kwargs):

        if isinstance(f, six.string_types):
            return gzip.open(f, mode=mode, **kwargs)
        else:
            return gzip.GzipFile(fileobj=f, mode=mode, **kwargs)


class BZ2(_BaseCompressionDriver):

    """
    Driver for accessing data stored as BZIP2.
    """

    driver_name = 'BZ2'
    extensions = 'bz2',

    def open(self, f, mode='r', **kwargs):

        """
        All arguments are passed directly to `bz2.BZFile()`.

        Parameters
        ----------
        f : str or file
            File path or open file-like object.
        mode : str, optional
            I/O mode for the `bz2` library.
        kwargs : **kwargs, optional
            Additional keyword arguments for `bz2.BZFile()`.
        """

        return bz2.BZ2File(f, mode=mode, **kwargs)


# Register external drivers
for ep in iter_entry_points('gpsdio.drivers'):
    try:
        ep.load()
        logger.debug("Loaded entry-point `%s'", ep.name)
    except Exception as e:
        logger.exception("Attempted to load entry-point `%s' but failed:", ep.name, exc_info=1)
