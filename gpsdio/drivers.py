#!/usr/bin/env python

"""
Drivers for reading and writing a variety of formats and compression.
"""


import bz2
from codecs import open as codecs_open
import gzip

import msgpack
import newlinejson
import six
import ujson


newlinejson.JSON = ujson


def get_driver(name):

    """
    Accepts a string and returns the driver class associated with that name.
    """

    if name in BaseDriver.by_name:
        return BaseDriver.by_name[name]
    else:
        raise ValueError("Unrecognized driver name: %s" % name)


def get_compression(name):

    """
    Accepts a string and returns the driver class associated with that name.
    """

    if name in BaseCompressionDriver.by_name:
        return BaseCompressionDriver.by_name[name]
    else:
        raise ValueError("Unrecognized compression name: %s" % name)


def detect_file_type(path):

    """
    Given an file path, attempt to determine appropriate driver.
    """

    for ext in path.split('.')[-2:]:
        if ext in BaseDriver.by_extension:
            return BaseDriver.by_extension[ext]
    else:
        raise ValueError("Can't determine driver: %s" % path)


def detect_compression_type(path):

    """
    Given a file path, attempt to determine the appropriate compression driver.
    """

    ext = path.rpartition('.')[-1]
    if ext in BaseCompressionDriver.by_extension:
        return BaseCompressionDriver.by_extension[ext]
    else:
        raise ValueError("Can't determine compression: %s" % path)


class _RegisterDriver(type):

    """
    Keep track of drivers, their names, and extensions for easy retrieval later.
    """

    def __init__(driver, name, bases, members):
        # TODO: Add validation.  What methods are required?
        """
        Register drivers by name in one dictionary and by extension in another.
        """

        type.__init__(driver, name, bases, members)
        if members.get('register', True):
            driver.by_name[driver.driver_name] = driver
            for ext in driver.extensions:
                driver.by_extension[ext] = driver


class BaseDriver(six.with_metaclass(_RegisterDriver, object)):

    """
    Provides driver registration and the baseline methods required for driver
    operation.  All other non-compression drivers must subclass this class if
    they want to be registered.  Compression drivers should subclass
    `BaseCompressionDriver()`.


    Creating a driver
    -----------------

    Generally speaking drivers behave just like an instance of `file`, except
    they operate on data stored in a very specific way.  Drivers must handle file
    opening, closing, reading, and writing, and must pass an object that behaves
    like `file` to `BaseDriver.__init__()`.  The really critical methods are
    `__iter__()` and `write()`.  The former must yield one dictionary per
    iteration and the latter must accept a dictionary and write it to disk.

    See the `NewlineJSON()` driver for an example of a really simple driver
    and the `MsgPack()` driver for one that is more complex.
    """

    by_name = {}
    by_extension = {}
    register = False
    io_modes = ('r', 'w', 'a')

    def __init__(self, stream):

        """
        Creates an object that transparently interacts with all supported drivers
        by calling `stream`'s methods.

        Parameters
        ----------
        stream : <object>
            An object provided by a driver that behaves like `file`.
        """

        self._stream = stream

    def __repr__(self):
        return "<%s driver %s, mode '%s'>" % (
            'closed' if self.closed else 'open',
            self.driver_name,
            self.mode
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        return iter(self.stream)

    @property
    def stream(self):

        """
        A handle to the underlying file-like object.  This can range from simply
        being an instance of `file()` to being an instance of a compression
        driver, which in turn has a `stream` property that is a driver class etc.
        """

        return self._stream

    def next(self):

        """
        This method must be explicitly defined, otherwise the `__getattr__()`
        method will return the `stream`'s `next()` method, which is not in the
        same namespace as `__iter__()` so this class will appear to have the
        necessary methods to be an iterator but will raise exceptions when
        iterated over.
        """

        return next(self.stream)

    __next__ = next

    def __getattr__(self, item):

        """
        For all other methods, just get it from the underlying `stream`.
        """

        return getattr(self.stream, item)


class NewlineJSON(BaseDriver):

    """
    Driver for accessing data stored as newline delimited JSON.
    """

    driver_name = 'NewlineJSON'
    extensions = ('json', 'nljson')

    def __init__(self, f, mode='r', **kwargs):

        """
        The object returned by `newlinejson.open()` has all of the methods
        required by `BaseDriver()` so this constructor is pretty sparse.  The
        `newlinejson.open()` function handles all of the file opening/closing
        and the returned object is passed directly to `BaseDriver()`.

        Parameters
        ----------
        f : str or `newlinejson.Stream()`
            Path to a file that can be opened by `newlinejson.open()` or a fully
            instantiated `newlinejson.Stream()` object.
        mode : str, optional
            I/O mode for `newlinejson.open()`.
        kwargs : **kwargs, optional
            Additional keyword arguments for `newlinejson.open()`.
        """

        BaseDriver.__init__(
            self,
            newlinejson.open(f, mode=mode, **kwargs)
        )


class MsgPack(BaseDriver):

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

    def __init__(self, f, mode='r', **kwargs):

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
            self._f = codecs_open(f, mode=mode)
        else:
            self._f = f
        if mode == 'r':
            BaseDriver.__init__(
                self,
                self._MsgPackReader(self._f, **kwargs)
            )
        else:
            BaseDriver.__init__(
                self,
                self._MsgPackWriter(self._f, **kwargs)
            )


class BaseCompressionDriver(BaseDriver):

    """
    A slightly modified subclass of `BaseDriver()` to allow separation of normal
    drivers and compression drivers.
    """

    by_name = {}
    by_extension = {}
    register = False


class GZIP(BaseCompressionDriver):

    """
    Driver for accessing data stored as GZIP.
    """

    driver_name = 'GZIP'
    extensions = 'gz',

    def __init__(self, f, mode='r', **kwargs):

        """
        Creates an instance of `gzip.GzipFile()` and passes it to `BaseDriver()`.

        If `f` is a string `gzip.open()` is used, otherwise `gzip.GzipFile()` is
        instantiated directly.

        Parameters
        ----------
        f : str or file
            File path or open file-like object.
        mode : str, optional
            I/O mode for the `gzip` library.
        kwargs : **kwargs, optional
            Additional keyword arguments for `gzip.open()` or `gzip.GzipFile()`.
        """

        if isinstance(f, six.string_types):
            BaseDriver.__init__(
                self,
                gzip.open(f, mode=mode, **kwargs)
            )
        else:
            BaseDriver.__init__(
                self,
                gzip.GzipFile(fileobj=f, mode=mode, **kwargs)
            )


class BZ2(BaseCompressionDriver):

    """
    Driver for accessing data stored as BZIP2.
    """

    driver_name = 'BZ2'
    extensions = 'bz2',

    def __init__(self, f, mode='r', **kwargs):

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

        BaseDriver.__init__(
            self,
            bz2.BZ2File(f, mode=mode, **kwargs)
        )
