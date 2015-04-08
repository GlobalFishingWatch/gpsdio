#!/usr/bin/env python

"""
Drivers for reading and writing a variety of formats and compression.
"""


import gzip

from .pycompat import *

import msgpack
import newlinejson
import ujson


newlinejson.JSON = ujson


def get_driver(name):

    """
    Accepts a string and returns the driver class associated with that name.
    """

    if name in BaseDriver.by_name and not BaseDriver.by_name[name].compression:
        return BaseDriver.by_name[name]
    else:
        raise ValueError("Unrecognized driver name: %s" % name)


def get_compression(name):

    """
    Accepts a string and returns the driver class associated with that name.
    """

    if name in BaseDriver.by_name and BaseDriver.by_name[name].compression:
        return BaseDriver.by_name[name]
    else:
        raise ValueError("Unrecognized compression name: %s" % name)


def detect_file_type(path):

    """
    Given an file path, attempt to determine appropriate driver.
    """

    for ext in path.split('.')[-2:]:
        if ext in BaseDriver.by_extension and not BaseDriver.by_extension[ext].compression:
            return BaseDriver.by_extension[ext]
    else:
        raise ValueError("Can't determine driver: %s" % path)


def detect_compression_type(path):

    """
    Given a file path, attempt to determine the appropriate compression driver.
    """

    ext = path.rpartition('.')[-1]
    if ext in BaseDriver.by_extension and BaseDriver.by_extension[ext].compression:
        return BaseDriver.by_extension[ext]
    else:
        raise ValueError("Can't determine compression: %s" % path)


class BaseDriver(object):

    by_name = {}
    by_extension = {}

    class __metaclass__(type):

        def __init__(driver, name, bases, members):
            type.__init__(driver, name, bases, members)
            if name != 'BaseDriver':
                driver.register_driver()

        def register_driver(driver):
            driver.validate_driver()
            BaseDriver.by_name[driver.name] = driver
            for ext in driver.extensions:
                BaseDriver.by_extension[ext] = driver

        def validate_driver(driver):
            assert isinstance(driver.name, str)
            assert isinstance(driver.extensions, (tuple, list))
            assert isinstance(driver.modes, (tuple, list))
            for attr in (
                    '__iter__', '__next__', 'read', 'write', 'modes', 'name', 'write', 'close', 'closed', 'read'):
                assert hasattr(driver, attr)

            return True

    def __init__(self, f, mode='r', modes=None, name=None, reader=None, writer=None, **kwargs):

        if isinstance(f, string_types):
            f = open(f, mode=mode)

        self._f = f
        self._modes = modes
        self._mode = mode
        self._name = name
        if mode == 'r':
            self.obj = reader(self._f, **kwargs)
        elif mode in ('w', 'a'):
            self.obj = writer(self._f, **kwargs)
        else:
            raise ValueError(
                "Mode `%s' is unsupported for driver %s: %s" % (mode, name, ', '.join(modes)) if modes else None)

    def __repr__(self):
        return "<%s driver %s, mode '%s', connected to '%r' at %s>" % (
            'closed' if self.closed else 'open',
            self.name,
            self.mode,
            self.obj,
            hex(id(self))
        )

    def __iter__(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def next(self):
        return next(self.obj)

    __next__ = next

    @property
    def modes(self):
        return self._modes

    @property
    def mode(self):
        return self._mode

    @property
    def name(self):
        return self._name

    def write(self, msg, **kwargs):
        return self.obj.write(msg, **kwargs)

    @property
    def closed(self):
        return self.obj.closed

    def close(self):
        self.obj.close()

    def read(self, size):
        return self.obj.read(size)


class NewlineJSON(BaseDriver):

    name = 'newlinejson'
    extensions = ('json', 'nljson')
    modes = ('r', 'w', 'a')
    compression = False

    def __init__(self, f, mode='r', **kwargs):

        BaseDriver.__init__(
            self,
            f=f, mode=mode,
            reader=newlinejson.Reader,
            writer=newlinejson.Writer,
            modes=self.modes,
            name=self.name,
            **kwargs
        )

    @property
    def closed(self):
        return self._f.closed

    def close(self):
        self._f.close()


class MsgPack(BaseDriver):

    name = 'msgpack'
    extensions = ('msg', 'msgpack')
    modes = ('r', 'w', 'a')
    compression = False

    def __init__(self, f, mode='r', **kwargs):

        class MsgPackWriter(object):

            def __init__(self, f, mode='r', **kwargs):
                self._f = f
                self.packer = msgpack.Packer(**kwargs)

            def write(self, msg):
                self._f.write(self.packer.pack(msg))

        BaseDriver.__init__(
            self,
            f=f, mode=mode,
            reader=msgpack.Unpacker,
            writer=MsgPackWriter,
            modes=self.modes,
            name=self.name,
            **kwargs
        )

    def close(self):
        self._f.close()

    @property
    def closed(self):
        return self._f.closed


class GZIP(BaseDriver):

    name = 'gzip'
    extensions = 'gz',
    modes = ('r', 'w', 'a')
    compression = True

    def __init__(self, f, mode='r', **kwargs):

        def reader(f, **kwargs):
            return gzip.GzipFile(fileobj=f, mode=mode, **kwargs)

        def writer(f, **kwargs):
            return gzip.GzipFile(fileobj=f, mode=mode, **kwargs)

        BaseDriver.__init__(
            self,
            f=f, mode=mode,
            reader=reader,
            writer=writer,
            modes=self.modes,
            name=self.name,
            **kwargs
        )

    def close(self):
        self.obj.close()
        self._f.close()


# class BZ2(BaseDriver):
#
#     name = 'bz2'
#     extensions = 'bz2',
#     modes = ('r', 'w', 'a')
#     compression = True
#
#     def __init__(self, f, mode='r', **kwargs):
#
#         BaseDriver.__init__(
#             self,
#             f=f, mode=mode,
#             reader=bz2.BZ2File,
#             writer=bz2.BZ2File,
#             modes=self.modes,
#             name=self.name,
#             **kwargs
#         )
#
#
# class TAR(BaseDriver):
#
#     name = 'tar'
#     extensions = 'tar',
#     modes = ('r', 'w', 'a')
#     compression = True
#
#     def __init__(self, f, mode='r', **kwargs):
#
#         BaseDriver.__init__(
#             self,
#             f=f, mode=mode,
#             reader=tarfile.open,
#             writer=tarfile.open,
#             modes=self.modes,
#             name=self.name,
#             **kwargs
#         )
