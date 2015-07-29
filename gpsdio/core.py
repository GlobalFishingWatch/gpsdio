"""Read and write the GPSD format.

The API mimics that of csv.DictReader/DictWriter and uses
`gpsdio.schema` to get schema details.
"""


import logging
import sys

import six

from . import schema


log = logging.getLogger('gpsdio')


builtin_open = open


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

    log.debug("Opening: %s" % path)

    do = do or {}
    co = co or {}
    dmode = dmode or mode
    cmode = cmode or mode

    # Input path is a file-like object
    if not isinstance(path, six.string_types):

        log.debug("Input path is a file-like object: %s", path)

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

    log.debug("Compression driver: %s", io_driver)
    log.debug("Driver: %s", comp_driver)
    
    if comp_driver:
        c_stream = comp_driver(path, mode=cmode, **co)
    else:
        c_stream = path
        
    stream = io_driver(c_stream, mode=dmode, **do)

    log.debug("Built base I/O stream: %s", stream)

    return Stream(stream, mode=mode, **kwargs)


class Stream(object):

    def __init__(self, stream, mode='r', force_msg=False, keep_fields=True, skip_failures=False, convert=True,
                 *args, **kwargs):

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
        self.force_msg = force_msg
        self.skip_failures = skip_failures
        self._mode = mode
        self.convert = convert
        self.keep_fields = keep_fields
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

    def next(self):

        if self.mode != 'r':
            raise IOError("Stream not open for reading")
        elif self.closed:
            raise IOError("Can't operate on a closed stream")

        line = None
        try:
            loaded = line = next(self._stream)
            if self.convert:
                loaded = schema.import_msg(line, skip_failures=self.skip_failures)
                if self.force_msg:
                    loaded = schema.force_msg(loaded, keep_fields=self.keep_fields)
            return loaded
        except StopIteration:
            raise
        except Exception as e:
            if not self.skip_failures:
                import traceback
                raise Exception("%s: %s: %s\n%s" % (getattr(self._stream, 'name', 'Unknown'), type(e), e, "    " + traceback.format_exc().replace("\n", "\n    ")))
            return {"__invalid__": {"__content__": line}}

    __next__ = next

    def close(self):
        return self._stream.close()

    def writeheader(self):

        """
        Write a file header if one is needed by the container format
        """

        if self.mode == 'a':
            raise IOError("Can't write header when appending")
        elif self.mode != 'w':
            raise IOError("Stream not open for writing")
        elif self.closed:
            raise IOError("Can't operate on a closed stream")

        return self._stream.writeheader()

    def write(self, msg):

        if self.mode not in ('w', 'a'):
            raise IOError("Stream not open for writing")
        elif self.closed:
            raise IOError("Can't operate on a closed stream")

        if not self.keep_fields and 'type' in msg:
            msg = {field: val for field, val in six.iteritems(msg)
                   if field in schema.get_default_msg(msg['type'])}

        if self.convert:
            if self.force_msg:
                msg = schema.force_msg(msg, keep_fields=self.keep_fields)
            msg = schema.export_msg(msg, skip_failures=self.skip_failures)

        self._stream.write(msg)

    def writelines(self, msgs):
        for msg in msgs:
            self.write(msg)

    # csv.DictWriter compatibility, don't remove :)
    writerow = write
    writerows = writelines


def filter(stream, expressions):

    """
    A generator to filter a stream of data with boolean Pythonic expressions.
    Multiple expressions can be provided but only messages that evaluate as
    `True` for all will be yielded.

    `eval()` is used for expression evaluation but it is given a modified global
    scope that doesn't include some blacklisted items like `exec()`, `eval()`, etc.

    Example:

        >>> import gpsdio
        >>> criteria = ("type in (1, 2, 3)", "lat' in msg", "mmsi == 366268061")
        >>> with gpsdio.open('sample-data/types.msg.gz') as stream:
        ...     for msg in gpsdio.filter(stream, criteria):
        ...        # Do something

    Parameter
    ---------
    stream : iter
        An iterable producing one message per iteration.
    expressions : str or tuple
        A single expression or multiple expressions to be applied to each
        message.  Only messages that pass all filters will be yielded

    Yields
    ------
    dict
        Messages that pass all expressions.
    """

    if isinstance(expressions, six.string_types):
        expressions = expressions,

    scope_blacklist = ('eval', 'compile', 'exec', 'execfile', 'builtin', 'builtins',
                       '__builtin__', '__builtins__', 'globals', 'locals')

    global_scope = {
        k: v for k, v in globals().items() if k not in ('builtins', '__builtins__')}
    global_scope['__builtins__'] = {
        k: v for k, v in globals()['__builtins__'].items() if k not in scope_blacklist}
    global_scope['builtins'] = global_scope['__builtins__']

    for msg in stream:
        local_scope = msg.copy()
        local_scope['msg'] = msg
        for expr in expressions:
            try:
                result = eval(expr, global_scope, local_scope)
            except NameError:
                # A message doesn't contain something in the expression so just force a failure
                result = False

            if not result:
                break
        else:
            yield msg


def sort(stream, field='timestamp'):

    """
    A generator to sort data by the specified field.  Requires the entire stream
    to be held in memory.  Messages lacking the specified field are dropped.

    Parameters
    ----------
    stream : iter
        Iterator producing one message per iteration.
    field : str, optional
        Field to sort by.  Defaults to sorting by `timestamp`.
    """

    queue = six.moves.queue.PriorityQueue()
    for msg in stream:
        if field in msg:
            queue.put((msg[field], msg))

    while not queue.empty():
        yield queue.get()[1]
