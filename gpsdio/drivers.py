#!/usr/bin/env python

"""
Drivers for reading and writing a variety of formats and compression.
"""


import bz2
import gzip
import logging
from pkg_resources import iter_entry_points
import sys

import msgpack
import newlinejson as nlj
import newlinejson.core
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
    Access data stored as newline delimited JSON.  Driver options are passed to
    ``newlinejson.open()``.

    https://github.com/geowurster/newlinejson
    """

    driver_name = 'NewlineJSON'
    extensions = ('json', 'nljson')

    def open(self, path, mode='r', **kwargs):
        if isinstance(path, nlj.core.Stream):
            return path
        else:
            return newlinejson.open(path, mode=mode, **kwargs)


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

    def __init__(self, path, **kwargs):

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
        self._f = path

    def write(self, msg):
        self._f.write(self._packer.pack(msg))

    def __getattr__(self, item):
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
        return getattr(self._f, item)


class MsgPack(_BaseDriver):

    """
    Read and write data stored as MsgPack.  When reading, driver options are
    passed to ``msgpack.Unpacker()`` and ``msgpack.Packer()`` when writing.

    https://github.com/msgpack/msgpack-python
    """

    driver_name = 'MsgPack'
    extensions = ('msg', 'msgpack')

    def open(self, path, mode='r', **kwargs):

        if isinstance(path, six.string_types):
            f = open(path, mode=mode)
        else:
            f = path

        if mode == 'r':
            return _MsgPackReader(f, **kwargs)
        else:
            return _MsgPackWriter(f, **kwargs)


class GZIP(_BaseCompressionDriver):

    """
    Access data stored as GZIP using Python's builtin ``gzip`` library.  Driver
    options are passed to ``gzip.open()``, unless the input path is a file-like
    object, in which case they are passed to ``gzip.GzipFile()``.

    https://docs.python.org/3/library/gzip.html
    """

    driver_name = 'GZIP'
    extensions = 'gz',

    def open(self, path, mode='r', **kwargs):

        # TODO: There's probably a workaround for this?  Not critical but would be cool.
        if path == sys.stdin:
            raise TypeError("GZIP can't read directly from stdin")
        elif isinstance(path, six.string_types):
            return gzip.open(path, mode=mode, **kwargs)
        elif isinstance(path, gzip.GzipFile):
            return path
        else:
            return gzip.GzipFile(fileobj=path, mode=mode, **kwargs)


class BZ2(_BaseCompressionDriver):

    """
    Access data stored as BZ2 with Python's builtin ``bz2`` library.  Driver
    options are passed to ``bz2.BZ2File()``.

    https://docs.python.org/3/library/bz2.html
    """

    driver_name = 'BZ2'
    extensions = 'bz2',

    def open(self, path, mode='r', **kwargs):

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

        if isinstance(path, bz2.BZ2File):
            return path
        else:
            return bz2.BZ2File(path, mode=mode, **kwargs)


# Register external drivers
for ep in list(iter_entry_points('gpsdio.drivers')) + list(iter_entry_points('gpsdio.driver_plugins')):
    try:
        ep.load()
        logger.debug("Loaded entry-point `%s'", ep.name)
    except Exception as e:
        logger.exception("Attempted to load entry-point `%s' but failed:", ep.name, exc_info=1)

# Import after loading external drivers to avoid creating a confusing condition
# in the logfile
from gpsdio.base import BaseDriver, BaseCompressionDriver

registered_drivers = BaseDriver.by_name
registered_compression = BaseCompressionDriver.by_name
