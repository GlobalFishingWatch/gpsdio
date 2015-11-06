"""
Base objects to avoid import errors.
"""


import datetime
import logging

import six

import gpsdio
from gpsdio.schema import datetime2str
from gpsdio.schema import build_validator
import voluptuous


logger = logging.getLogger('gpsdio')


class GPSDIOBaseStream(object):

    def __init__(self, stream, mode='r', schema=None, _validator=None, _check=True):

        """
        Read or write a stream of AIS data.

        Parameters
        ----------
        stream : file-like object or iterable
            Expects one dictionary per iteration.
        mode : str, optional
            Determines if stream is operating in read, write, or append mode.

        Experimental Parameters
        -----------------------
        _validator : dict, optional
            A dictionary that matches the output of `build_validator()`.  Can
            be used to bypass building a full schema.
        _check : bool, optional
            Should messages be checked against the schema?

        Returns
        -------
        GPSDIOReader
            If a read mode is used.
        GPSDIOWriter
            If a write mode is used.
        """

        if schema and _validator:
            raise ValueError("Cannot supply both schema and validator.")

        self._schema = schema
        self._validator = _validator or build_validator(self._schema)
        self._stream = stream
        self._iterator = stream
        self._check = _check
        self._mode = mode

    @property
    def schema(self):
        return self._schema

    def validate_msg(self, msg):

        """
        Validate a message against the supplied schema.

        Parameters
        ----------
        msg : dict
            GPSd message.

        Raises
        ------
        ValueError
            Message does not match schema.

        Returns
        -------
        dict
            GPSd message.
        """

        if self._check:
            try:
                return {n: v(msg[n]) for n, v in six.iteritems(self._validator[msg['type']])}
            except KeyError as e:
                raise ValueError("Missing field '{}' from message: {}".format(e.args[0], msg))
            except (gpsdio.schema.Invalid, voluptuous.Invalid) as e:
                raise ValueError("{e}: {msg}".format(e=str(e), msg=str(msg)))
        else:
            return msg

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stream.close()

    @property
    def closed(self):
        return self._stream.closed

    @property
    def mode(self):
        return self._mode

    @property
    def name(self):
        return getattr(self._stream, 'name', '<unknown name>')

    def close(self):

        """
        Close the underlying stream and flush to disk.
        """

        return self._stream.close()


class _DriverRegistry(type):

    """
    Keep track of drivers, their names, and extensions for easy retrieval later.
    """

    def __init__(driver, name, bases, members):

        """
        Register drivers by name in one dictionary and by extension in another.
        """

        # TODO: Add validation.  What methods are required?

        type.__init__(driver, name, bases, members)
        if driver.driver_name not in ('BaseDriver', 'BaseCompressionDriver'):
            driver.by_name[driver.driver_name] = driver
            for ext in driver.extensions:
                driver.by_extension[ext] = driver


class BaseDriver(six.with_metaclass(_DriverRegistry, object)):

    by_name = {}
    by_extension = {}
    driver_name = 'BaseDriver'  # Use driver_name to prevent a file.name collision

    def __init__(self, schema=None):
        self._f = None
        self._schema = schema
        self._mode = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __next__(self):
        return self.load(next(self.f))

    next = __next__

    def write(self, msg):
        return self.f.write(self.dump(msg))

    @property
    def name(self):
        return self._f.name

    @property
    def f(self):
        return self._f

    @property
    def mode(self):
        return self._f.mode

    @property
    def io_modes(self):
        raise NotImplementedError

    @property
    def schema(self):
        return self._schema

    @property
    def closed(self):
        return self.f.closed

    def load(self, msg):

        """
        Drivers should override this method if they have special handling for
        specific types.  This implementation assumes the line read from disk
        is ready to be validated.

        Parameters
        ----------
        msg : dict
            GPSd message.

        Returns
        -------
        dict
            GPSd message.
        """

        return msg

    def dump(self, msg):

        """
        Serialize message to be flushed to disk.  Converts datetimes to str.
        Drivers should override this method if they have special handling for
        specific types.  This implementation assumes the driver wants everything
        to be an `int`, `float`, or `str`.

        Parameters
        ----------
        msg : dict
            GPSd message.

        Returns
        -------
        dict
            GPSd message with serialized values.
        """

        return {k: datetime2str(v) if isinstance(v, datetime.datetime) else v
                for k, v in six.iteritems(msg)}

    def start(self, name, mode='r', **kwargs):
        if mode not in self.io_modes:
            raise ValueError(
                "I/O mode '{m}' unsupported: {modes}".format(m=mode, modes=self.io_modes))
        self._f = self.open(name=name, mode=mode, **kwargs)
        self._mode = mode

    def stop(self):
        self.close()

    def close(self):
        return self._f.close()

    def open(self, name, mode, **kwargs):
        raise NotImplementedError


class BaseCompressionDriver(BaseDriver):

    """
    A slightly modified subclass of `BaseDriver()` to allow separation of normal
    drivers and compression drivers.
    """

    by_name = {}
    by_extension = {}
    driver_name = 'BaseCompressionDriver'

    def open(self, name, mode, **kwargs):
        raise NotImplementedError

    def dump(self, msg):
        return msg

    def load(self, msg):
        return msg
