"""
Read and write the GPSD format. The API mimics
that of csv.DictReader/DictWriter and uses gpsd_format.schema to get schema details
"""


import logging

import six

from . import drivers
from . import schema
from .pycompat import *


log = logging.getLogger('gpsd_format')


builtin_open = open


__all__ = ['open', 'Stream']


def open(path, mode='r', dmode=None, cmode=None, compression=None, driver=None, do=None, co=None, **kwargs):

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

    # Normalize driver options, compression options, driver mode, and compression mode
    if do is None:
        do = {}
    if co is None:
        co = {}
    if dmode is None:
        dmode = mode
    if cmode is None:
        cmode = mode

    if isinstance(compression, string_types):
        comp_driver = drivers.get_compression(compression)
    elif compression is None:
        try:
            comp_driver = drivers.detect_compression_type(getattr(path, 'name', path))
        except ValueError:
            comp_driver = None
    else:
        comp_driver = None

    if isinstance(driver, string_types):
        io_driver = drivers.get_driver(driver)
    else:
        io_driver = drivers.detect_file_type(getattr(path, 'name', path))

    if comp_driver:
        stream = io_driver(comp_driver(path, mode=cmode, **co), mode=dmode, **do)
    else:
        stream = io_driver(path, mode=dmode, **do)

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


# def info(stream, invalid_key=schema.DEFAULT_INVALID_KEY):
#
#     """
#     Get a report about a chunk of AIS data.  Report is a dictionary with the
#     following keys:
#
#         lon_min (float) -> Minimum 'lon' value
#         lon_max (float) -> Maximum 'lon' value
#         lat_min (float) -> Maximum 'lat' value
#         lat_max (float) -> Minimum 'lat' value
#         num_rows (int)   -> Total number of rows in input file
#         num_invalid_rows -> Number of malformed rows
#         mmsi_hist (dict) -> {mmsi: number of rows with that MMSI}
#         is_sorted (bool) -> Specifies whether the entire file is sorted by timestamp
#         msg_type_hist (dict) -> {message_type: number of rows with that type}
#         min_timestamp (datetime) -> Earliest timestamp
#         max_timestamp (datetime) -> Latest timestamp
#         mmsi_declaration (bool) -> Whether an MMSI specified in the filename
#             with mmsi=NUMBER is the only mmsi inside the file.
#
#     Example output:
#
#         {
#             'num_rows': 999,
#             'num_invalid_rows': 18,
#             'lat_min': -52.502449999999996,
#             'lat_max': 70.80154666666668,
#             'lon_min': -165.8861,
#             'lon_max': 153.36407833333334,
#             'min_timestamp': datetime.datetime(2014, 11, 1, 7, 59, 23),
#             'max_timestamp': datetime.datetime(2014, 11, 1, 7, 59, 31),
#             'is_sorted': True,
#             'mmsi_declaration': None,
#             'mmsi_hist': {
#                 '371067000': 1,
#                 '203999339': 1,
#                 '224142870': 5,
#                 '413505670': 2,
#                 '316001649': 1,
#                 ...
#             },
#             'msg_type_hist': {
#                 1: 416,
#                 2: 3,
#                 3: 155,
#                 5: 425
#             }
#         }
#
#     Parameters
#     ----------
#     input : iterable
#         An open GPSDReader or other iterable over messages
#     verbose : bool, optional
#         When an invalid row is encountered, print an error to `err`
#     err : file, optional
#         Stream where errors are written if `verbose=True`
#
#     Returns
#     -------
#     dict
#     """
#
#     stats = {
#         'lon_min': None,
#         'lon_max': None,
#         'lat_min': None,
#         'lat_max': None,
#         'count': 0,
#         'mmsi_hist': {},
#         'msg_type_hist': {},
#         'num_incomplete_msgs': 0,
#         'num_invalid_msgs': 0,
#         'is_sorted': True,
#         'min_timestamp': None,
#         'max_timestamp': None,
#         # 'mmsi_declaration': None
#     }
#
#     # mmsi_declaration = None
#     # if input.name is not None and 'mmsi=' in input.name:
#     #     mmsi_declaration = re.findall(r"mmsi=([^,.]*)[.,]", input.name)[0]
#     #     stats['mmsi_declaration'] = True
#
#     previous_timestamp = None
#     for msg in stream:
#
#         # num_msgs
#         stats['count'] += 1
#
#         # lon_min
#         if 'lon' in msg and (stats['lon_min'] is None or msg['lon'] < stats['lon_min']):
#             stats['lon_min'] = msg['lon']
#
#         # lon_max
#         if 'lon' in msg and (stats['lon_max'] is None or msg['lon'] > stats['lon_max']):
#             stats['lon_max'] = msg['lon']
#
#         # lat_min
#         if 'lat' in msg and (stats['lat_min'] is None or msg['lat'] < stats['lat_min']):
#             stats['lat_min'] = msg['lat']
#
#         # lat_max
#         if 'lat' in msg and (stats['lat_max'] is None or msg['lat'] > stats['lat_max']):
#             stats['lat_max'] = msg['lat']
#
#         # mmsi_hist
#         if 'mmsi' in msg:
#             if msg['mmsi'] in stats['mmsi_hist']:
#                 stats['mmsi_hist'][msg['mmsi']] += 1
#             else:
#                 stats['mmsi_hist'][msg['mmsi']] = 1
#
#             # if mmsi_declaration is not None:
#             #     if str(msg['mmsi']) != mmsi_declaration:
#             #         stats['mmsi_declaration'] = False
#
#         # msg_type_hist
#         if 'type' in msg:
#             if msg['type'] in stats['msg_type_hist']:
#                 stats['msg_type_hist'][msg['type']] += 1
#             else:
#                 stats['msg_type_hist'][msg['type']] = 1
#
#         # min_timestamp
#         if 'timestamp' in msg and (stats['min_timestamp'] is None or msg['timestamp'] < stats['min_timestamp']):
#             stats['min_timestamp'] = msg['timestamp']
#
#         # max_timestamp
#         if 'timestamp' in msg and (stats['max_timestamp'] is None or msg['timestamp'] > stats['max_timestamp']):
#             stats['max_timestamp'] = msg['timestamp']
#
#         # is_sorted
#         # This only executes if stats['is_sorted'] = True in order to gain
#         # a little optimization.  No need to test if we already know its not sorted.
#         if previous_timestamp is not None and stats['is_sorted'] and 'timestamp' in msg:
#             if not msg['timestamp'] >= previous_timestamp:
#                 stats['is_sorted'] = False
#
#         # num_invalid_msgs
#         if not schema.validate_msg(msg, invalid_key=invalid_key):
#             stats['num_invalid_msgs'] += 1
#
#     return stats


# def as_geojson(iterator, x_field='longitude', y_field='latitude'):
#
#     """
#     Convert GPSD to GeoJSON Points on the fly.
#
#     Parameters
#     ----------
#     iterator : iterable object
#         An iterable object that produces one GPSD message per iteration.
#     x_field : str, optional
#         Field containing longitude.  Will be converted to a GeoJSON point and
#         removed from the output.
#     y_field : str, optional
#         Field containing latitude.  Will be converted to a GeoJSON point and
#         removed from the output.
#     """
#
#     for idx, row in enumerate(iterator):
#         o = {
#             'id': idx,
#             'type': 'Feature',
#             'properties': {k: v for k, v in row.items() if k not in (x_field, y_field)},
#             'geometry': {
#                 'type': 'Point',
#                 'coordinates': (row[x_field], row[y_field])
#             }
#         }
#         del o[x_field]
#         del o[y_field]
#         yield o
#
#
# def from_geojson(iterator, x_field='longitude', y_field='latitude'):
#
#     """
#     Convert GeoJSON Points to GPSD on the fly.
#
#     Parameters
#     ----------
#     iterator : iterable object
#         An iterable object that produces one GeoJSON Point message per iteration.
#         Note that
#     x_field : str, optional
#         Write longitude to this field - will be overwritten if it already exists.
#     y_field : str, optional
#         Write latitude to this field - will be overwritten if it already exists.
#
#     Raises
#     ------
#     TypeError
#         Input object isn't a GeoJSON Point.
#
#     Yields
#     ------
#     dict
#         GPSD message.
#     """
#
#     for feature in iterator:
#
#         if feature['geometry']['type'] != 'Point':
#             raise TypeError("Input object is not a GeoJSON point: %s" % feature)
#
#         point = feature['geometry']['coordinates']
#         o = feature['properties']
#         o[x_field] = point[0]
#         o[y_field] = point[1]
#
#         yield o
