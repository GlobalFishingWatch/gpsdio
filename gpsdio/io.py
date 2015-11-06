"""
Core components for Pythonic message I/O.


with gpsdio.open(infile) as src, gpsdio.open(outfile, 'w') as dst:
    for msg in src:
        dst.write(msg
"""


import logging
import os
import sys

import six

import gpsdio.base
import gpsdio.schema


logger = logging.getLogger('gpsdio')


def open(
        name,
        mode='r',
        compression=None,
        driver=None,
        do=None,
        co=None,
        schema=None,
        **kwargs):

    """
    Return a `Stream`() instance that is set up to read or write with the
    specified driver.

    Parameters
    ----------
    path : str
        File to be opened.
    mode : str, optional
        Mode to open both the file and driver with.
    compression : str, optional
        Read or write compressed data by specifying a compression type.
    driver : str, optional
        Read or write data with this driver.
    do : dict, optional
        Additional options to pass to the driver.
    co : dict, optional
        Additional options to pass to the compression driver.
    kwargs : **kwargs, optional
        Additional options to pass to `Stream()`.

    Returns
    -------
    Stream
        A loaded instance of stream ready for I/O operations.
    """

    # Drivers have to be imported inside open in order to prevent an import
    # collision when registering external drivers.
    from gpsdio.drivers import _COMPRESSION
    from gpsdio.drivers import _COMPRESSION_BY_EXT
    from gpsdio.drivers import _DRIVERS
    from gpsdio.drivers import _DRIVERS_BY_EXT

    if name == '-' and 'r' in mode:
        logger.debug("")
        name = sys.stdin
    elif name == '-' and mode in ('w', 'a'):
        name = sys.stdout

    logger.debug("Opening '%s' with mode '%s'", name, mode)

    # Handle defaults
    do = do or {}
    co = co or {}
    schema = schema or gpsdio.schema.build_schema()

    in_name = name if isinstance(name, six.string_types) else getattr(name, 'name', None)

    # Disable compression checks with False
    if compression is False:
        logger.debug("Disabled auto-checking compression")
        cmp_driver = None

    # User explicitly supplied a compression name
    elif compression is not None:
        logger.debug("User says the compression is '%s'", compression)
        cmp_driver = _COMPRESSION[compression]

    # Detect compression
    else:
        cmp_driver = None
        logger.debug("Detecting compression ...")
        ext = os.path.splitext(in_name)[1].strip('.')
        if ext in _DRIVERS_BY_EXT:
            logger.debug("Skipping compression - not given and extension matches a driver")
        elif not ext:
            logger.debug("Input file doesn't have an extension - assuming no compression")
        else:
            cmp_driver = _COMPRESSION_BY_EXT[ext]
            logger.debug("Detected compression as '%s'", cmp_driver.name)

    # User explicitly specified a driver by name
    if driver is not None:
        logger.debug("User says the driver is '%s'", driver)
        io_driver = _DRIVERS[driver]

    # Detect driver
    else:
        logger.debug("Detecting driver ...")
        _path, ext = os.path.splitext(in_name)
        if ext.strip('.') in _COMPRESSION_BY_EXT:
            _path, ext = os.path.splitext(_path)
        io_driver = _DRIVERS_BY_EXT[ext.strip('.')]
        logger.debug("Successfully detected driver")

    logger.debug("compression driver: %s", cmp_driver)
    logger.debug("I/O driver: %s", io_driver)

    if cmp_driver:
        cmp_stream = cmp_driver()
        cmp_stream.start(name=name, mode=mode, **co)
        logger.debug("Started compression stream")
    else:
        cmp_stream = name

    stream = io_driver(schema=schema)
    stream.start(name=cmp_stream, mode=mode, **do)
    logger.debug("Started I/O stream")

    if mode == 'r':
        logger.debug("Starting read session")
        return GPSDIOReader(stream, mode=mode, schema=schema, **kwargs)
    elif mode in ('w', 'a'):
        logger.debug("Starting write or append session")
        return GPSDIOWriter(stream, mode=mode, schema=schema, **kwargs)
    else:
        raise ValueError("Mode '{}' is invalid.".format(mode))


class GPSDIOReader(gpsdio.base.GPSDIOBaseStream):

    """
    Read GPSd messages.  Some overhead is removed by abstracting this class,
    which can be significant when multiplied across a large number of messages.
    """

    def __iter__(self):
        return self

    def __next__(self):

        """
        Get a GPSd message from the driver and validate.
        """

        if self.closed:
            raise IOError("Cannot operate on a closed stream.")

        return self.validate_msg(next(self._iterator))

    next = __next__


class GPSDIOWriter(gpsdio.base.GPSDIOBaseStream):

    """
    Write GPSd messages.  Some overhead is removed by abstracting this class,
    which can be significant when multiplied across a large number of messages.
    """

    def write(self, msg):

        """
        Validate and write a message to disk.

        Parameters
        ----------
        msg : dict
            GPSd message.
        """

        if self.closed:
            raise IOError("Cannot operate on a closed stream.")

        return self._stream.write(self.validate_msg(msg))
