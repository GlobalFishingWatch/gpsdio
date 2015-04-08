#!/usr/bin/env python

"""
Drivers for reading and writing a variety of formats and compression.
"""


from .pycompat import *

import msgpack
import newlinejson
import ujson


newlinejson.JSON = ujson


# def get_driver(name):
#
#     """
#     Accepts a string and returns the driver class associated with that name.
#     """
#
#     for d in REGISTERED_DRIVERS:
#         if d.name == name:
#             return d
#     else:
#         raise ValueError("Unrecognized driver name: %s" % name)
#
#
# def get_compression(name):
#
#     """
#     Accepts a string and returns the driver class associated with that name.
#     """
#
#     for d in COMPRESSION_DRIVERS:
#         if d.name == name:
#             return d
#     else:
#         raise ValueError("Unrecognized compression name: %s" % name)
#
#
# def detect_file_type(path):
#
#     """
#     Given an file path, attempt to determine appropriate driver.
#     """
#
#     for d in REGISTERED_DRIVERS:
#         for ext in path.split('.')[-2:]:
#             if ext in d.extensions:
#                 return d
#     else:
#         raise ValueError("Can't determine driver: %s" % path)
#
#
# def detect_compression_type(path):
#
#     """
#     Given a file path, attempt to determine the appropriate compression driver.
#     """
#
#     for d in COMPRESSION_DRIVERS:
#         if path.rpartition('.')[-1] in d.extensions:
#             return d
#     else:
#         raise ValueError("Can't determine compression: %s" % path)


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

    register = False

    class __metaclass__(type):
        def __init__(driver, name, bases, members):
            type.__init__(driver, name, bases, members)
            if members.get('register', True):
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

    def __init__(self, f, mode='r', modes=None, name=None, **kwargs):
        self._f = f
        self._modes = modes
        self._mode = mode
        self._name = name
        self.obj = None

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


class FileDriver(BaseDriver):
    register = False

    def __init__(self, *args, **kwargs):
        BaseDriver.__init__(self, *args, **kwargs)

        if isinstance(self._f, string_types):
            self._f = open(self._f, mode=self.mode)

        if self.mode == 'r':
            self.obj = self.reader(self._f, **kwargs)
        elif self.mode in ('w', 'a'):
            self.obj = self.writer(self._f, **kwargs)
        else:
            raise ValueError(
                "Mode `%s' is unsupported for driver %s: %s" % (self.mode, self.name, ', '.join(self.modes)) if self.modes else None)

    def close(self):
        self.obj.close()
        self._f.close()


class NewlineJSON(FileDriver):
    name = 'newlinejson'
    extensions = ('json', 'nljson')
    modes = ('r', 'w', 'a')
    compression = False

    def reader(self, f, *args, **kwargs):
        return newlinejson.Reader(f)

    def writer(self, f, *args, **kwargs):
        return newlinejson.Writer(f)

    @property
    def closed(self):
        return self._f.closed

    def close(self):
        self._f.close()


class MsgPack(FileDriver):
    name = 'msgpack'
    extensions = ('msg', 'msgpack')
    modes = ('r', 'w', 'a')
    compression = False


    class MsgPackWriter(object):
        def __init__(self, f, mode='r', **kwargs):
            self._f = f
            self.packer = msgpack.Packer(**kwargs)

        def write(self, msg):
            self._f.write(self.packer.pack(msg))


    def reader(self, f, *args, **kwargs):
        return msgpack.Unpacker(f)

    def writer(self, f, *args, **kwargs):
        return self.MsgPackWriter(f, *args, **kwargs)

    def close(self):
        self._f.close()

    @property
    def closed(self):
        return self._f.closed

try:
    import gzip
except:
    pass
else:
    class GZIP(FileDriver):
        name = 'gzip'
        extensions = 'gz',
        modes = ('r', 'w', 'a')
        compression = True

        def reader(self, f, *args, **kwargs):
            return gzip.GzipFile(fileobj=f, *args, **kwargs)

        def writer(self, f, *args, **kwargs):
            return gzip.GzipFile(fileobj=f, *args, **kwargs)

try:
    import lzma
except:
    pass
else:
    class LZMA(BaseDriver):
        name = 'lzma'
        extensions = 'xz',
        modes = ('r', 'w', 'a')
        compression = True

        def __init__(self, f, mode='r', **kwargs):
            BaseDriver.__init__(self, f, mode=mode, **kwargs)
            self.obj = lzma.LZMAFile(self._f, mode)
            

try:
    import bz2
except:
    pass
else:
    class BZ2(BaseDriver):
        name = 'bz2'
        extensions = 'bz2',
        modes = ('r', 'w', 'a')
        compression = True

        def __init__(self, f, mode='r', **kwargs):
            BaseDriver.__init__(self, f, mode=mode, **kwargs)
            self.obj = bz2.BZ2File(self._f, mode, **kwargs)

# class TAR(FileDriver):
#
#     name = 'tar'
#     extensions = 'tar',
#     modes = ('r', 'w', 'a')
#     compression = True
#
#     def __init__(self, f, mode='r', **kwargs):
#
#         FileDriver.__init__(
#             self,
#             f=f, mode=mode,
#             reader=tarfile.open,
#             writer=tarfile.open,
#             modes=self.modes,
#             name=self.name,
#             **kwargs
#         )


# def validate_driver(driver):
#     assert isinstance(driver.name, str)
#     assert isinstance(driver.extensions, (tuple, list))
#     assert isinstance(driver.modes, (tuple, list))
#     for attr in (
#             '__iter__', '__next__', 'read', 'write', 'from_path', 'modes', 'name', 'write', 'close', 'closed', 'read'):
#         assert hasattr(driver, attr)
#
#     return True


# TODO: Make this a function that does some baseline driver validation and logs when a driver can't be registered
# Keep track of every driver that is registered, just the ones the normal API cares about, and just the ones that are
# used for compression IO.
# ALL_REGISTERED_DRIVERS = FileDriver.__subclasses__()
# REGISTERED_DRIVERS = [
#     d for d in ALL_REGISTERED_DRIVERS if getattr(d, 'register', True) and not getattr(d, 'compression', False)]
# COMPRESSION_DRIVERS = [d for d in ALL_REGISTERED_DRIVERS if getattr(d, 'compression', False)]
