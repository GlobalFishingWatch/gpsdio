"""
Core components for Pythonic message I/O.


with gpsdio.open(infile) as src, gpsdio.open(outfile, 'w') as dst:
    for msg in src:
        dst.write(msg
"""


import logging
import sys

import six

from gpsdio import schema


logger = logging.getLogger('gpsdio')


__all__ = ['open', 'Stream']


def open(path, mode='r', dmode=None, cmode=None, compression=None, driver=None,
         do=None, co=None, **kwargs):

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
    from gpsdio.drivers import detect_compression_type
    from gpsdio.drivers import detect_file_type
    from gpsdio.drivers import registered_compression
    from gpsdio.drivers import registered_drivers

    if path == '-' and 'r' in mode:
        path = sys.stdin
    elif path == '-' and ('w' in mode or 'a' in mode):
        path = sys.stdout

    logger.debug("Opening: %s" % path)

    do = do or {}
    co = co or {}
    dmode = dmode or mode
    cmode = cmode or mode

    # Input path is a file-like object
    if not isinstance(path, six.string_types):

        logger.debug("Input path is a file-like object: %s", path)

        # If we get a driver name, just use that
        # Otherwise, detect it from the object's path property
        # If that doesn't work, crash because we don't know what to do
        if driver:
            io_driver = registered_drivers[driver]
        else:
            io_driver = detect_file_type(getattr(path, 'name', None))

        # Don't be too strict about compression.  At some point the driver
        # will try to read or write, which will throw an error if its really
        # a compressed file.
        if compression:
            comp_driver = registered_compression[compression]
        else:
            comp_driver = None

    # Input path is a string
    else:

        if driver:
            io_driver = registered_drivers[driver] 
        else:
            io_driver = detect_file_type(path)
        
        if compression:
            comp_driver = registered_compression[compression]
        else:
            # We cannot allow driver to fail, but detect_compression_type()
            # failing probably means that the file just isn't compressed
            try:
                comp_driver = detect_compression_type(path)
            except ValueError:
                comp_driver = None

    logger.debug("Compression driver: %s", io_driver)
    logger.debug("Driver: %s", comp_driver)
    
    if comp_driver:
        c_stream = comp_driver(path, mode=cmode, **co)
    else:
        c_stream = path
        
    stream = io_driver(c_stream, mode=dmode, **do)

    logger.debug("Built base I/O stream: %s", stream)

    if mode == 'r':
        logger.debug("Starting read session")
        return GPSDIOReader(stream, mode=mode, **kwargs)
    elif mode in ('w', 'a'):
        logger.debug("Starting write or append session")
        return GPSDIOWriter(stream, mode=mode, **kwargs)
    return GPSDIOBaseStream(stream, mode=mode, **kwargs)


class GPSDIOBaseStream(object):

    def __init__(self, stream, mode='r', convert=True, skip_failures=False):

        """
        Read or write a stream of AIS data.

        Parameters
        ----------
        stream : file-like object or iterable
            Expects one dictionary per iteration.
        mode : str, optional
            Determines if stream is operating in read, write, or append mode.
        force_message : bool, optional

        """

        self._stream = stream
        self.skip_failures = skip_failures
        self._mode = mode
        self.convert = convert
        self.skip_failures = skip_failures

    def __iter__(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stream.close()

    def __repr__(self):
        return "<%s Stream '%r', mode '%s' at %s>" % (
            "closed" if self.closed else "open",
            self._stream,
            self.mode,
            hex(id(self))
        )

    @property
    def closed(self):
        return self._stream.closed

    @property
    def mode(self):
        return self._mode

    @property
    def name(self):
        return getattr(self._stream, 'name', None)

    def close(self):

        """
        Close the underlying stream and flush to disk.
        """

        return self._stream.close()


class GPSDIOReader(GPSDIOBaseStream):

    """
    Read GPSd messages.  Some overhead is removed by abstracting this class,
    which can be significant when multiplied across a large number of messages.
    """

    def __init__(self, *args, **kwargs):

        """
        Instantiate a reader object and make sure the I/O mode matches.
        """

        assert kwargs['mode'] == 'r', \
            "{name} can only read data.".format(self.__class__.__name__)
        super(GPSDIOReader, self).__init__(*args, **kwargs)

    def __next__(self):

        try:

            msg = next(self._stream)

            if self.convert:
                msg = {
                    fld: schema.schema_import_functions.get(fld, lambda x: x)(v)
                    for fld, v in six.iteritems(msg)}

            return msg

        except StopIteration:
            raise

        except Exception as e:
            # TODO: Include a traceback for better error handling
            logger.exception(str(e))
            if not self.skip_failures:
                raise e

    next = __next__


class GPSDIOWriter(GPSDIOBaseStream):

    """
    Write GPSd messages.  Some overhead is removed by abstracting this class,
    which can be significant when multiplied across a large number of messages.
    """

    def __init__(self, *args, **kwargs):

        """
        Instantiate a writer object and make sure the I/O mode matches.
        """

        assert kwargs['mode'] in ('w', 'a'), \
            "{name} can only write and append data.".format(self.__class__.__name__)
        super(GPSDIOWriter, self).__init__(*args, **kwargs)

    def write(self, msg):

        """
        Write a message to disk.
        """

        try:

            if self.convert:
                msg = {
                    fld: schema.schema_export_functions.get(fld, lambda x: x)(v)
                    for fld, v in six.iteritems(msg)}

            self._stream.write(msg)

        except Exception as e:
            logger.exception(str(e))
            if not self.skip_failures:
                raise e
