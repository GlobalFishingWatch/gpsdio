"""
Read and write the GPSD format. The API mimics
that of csv.DictReader/DictWriter and uses gpsd_format.schema to get schema details
"""


import json
try:
    import msgpack
except ImportError:
    msgpack = None

import six

from . import schema


__all__ = ['ContainerFormat', 'GPSDReader', 'GPSDWriter']


class ContainerFormat(object):
    """Container format registry

    Each container format has a reader and a writer class.

    The reader class should be an iterator, and the writer have the
    method writerow(dict) and optionally writeheader()

    In addition both classes should have the method close() and the
    attributes closed (bool) and name (str)
    """

    formats = {}

    @classmethod
    def register(cls, name, reader, writer):
        cls.formats[name] = {'reader':reader, 'writer': writer}

    @classmethod
    def get(cls, format, usage='reader'):
        return cls.formats[format][usage]

    @classmethod
    def open(cls, file, options={}, format=None, usage='reader'):
        if format is None and hasattr(file, 'name'):
            format = file.name.rsplit(".", 1)[1]
        if format is None:
            format = 'json'
        return cls.get(format, usage)(file, **options)

class GPSDReader(object):
    def __init__(self, reader, force_message=False, keep_fields=True, throw_exceptions=True, convert=True,
                 *args, **kwargs):
        """
        Read the GPSD format. The API mimics that of
        csv.DictReader.

        Parameters
        ----------
        reader : iterator over dictionaries
            An iterator over dictionaries, possibly loaded using some container format
            (See the ContainerFormat class)
        force_message : bool
            Force rows being read to adhere to their specified AIS message
            type.  See `gpsd_format.schema.row2message()` for more information
        keep_fields : list or None
            Used by `gpsd_format.schema.row2message()` to allow keeping fields that
            do not adhere to the row's message type
        throw_exceptions: bool
            If true, reading a row with an attribute value that does not match
            the schema type for that attribute will cause an exception.
        convert: bool
            If false, don't convert attribute values not natively converted by the
            container format (e.g. dates)
        *args
            Collect and ignore additional positional arguments so the reader can
            be swapped with other readers that might take additional arguments
        **kwargs
            See `args`
        """

        self.reader = reader
        self.convert = convert
        self.force_message = force_message
        self.keep_fields = keep_fields
        self.throw_exceptions = throw_exceptions

    @classmethod
    def open(cls, f, format=None, format_options={}, *args, **kwargs):
        """
        Read the GPSD format from a file using one of the registered container formats.

        Parameters
        ----------
        f : file
            An open file object
        format: 'json' | 'msgpack'
            The name of a container format registered with ContainerFormat
        format_options: dict
            Dictionary with optional arguments for the container format reader
        Any additional arguments are passed directly on to __init__.

        """

        return cls(
            ContainerFormat.open(f, format=format, usage='reader'),
            *args, **kwargs)

    def __iter__(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __next__(self):
        return self.next()

    @property
    def closed(self):
        """
        Indicates whether or not the file object being read from is closed

        Returns
        -------
        bool
        """

        return self.reader.closed

    def next(self):
        """
        Get the next non-empty line in the file

        Returns
        -------
        dict
        """

        line = None
        try:
            loaded = line = next(self.reader)
            if self.convert:
                loaded = schema.import_msg(line, throw_exceptions=self.throw_exceptions)
                if self.force_message:
                    loaded = schema.row2message(loaded, keep_fields=self.keep_fields)
            return loaded
        except StopIteration:
            raise
        except Exception as e:
            if self.throw_exceptions:
                raise Exception("%s: %s: %s" % (getattr(self.reader, 'name', 'Unknown'), type(e), e))
            return {"__invalid__": {"__content__": line}}

    def close(self):

        """
        Close the file object being read from

        Returns
        -------
        None
        """

        self.reader.close()


class GPSDWriter(object):
    def __init__(self, writer, force_message=False, keep_fields=True, throw_exceptions=True, convert=True,
                 *args, **kwargs):
        """
        Write the GPSD format. The API mimics that of
        csv.DictWriter.

        Parameters
        ----------
        writer : object with method writerow(dict)
            An object to send encoded dictionaries to
        force_message : bool
            Force rows being written to adhere to their specified AIS message
            type.  See `gpsd_format.schema.row2message()` for more information
        keep_fields : list or None
            Used by `gpsd_format.schema.row2message()` to allow keeping fields that
            do not adhere to the row's message type
        throw_exceptions: bool
            If true, writing a row with an attribute value that does not match
            the schema type for that attribute will cause an exception.
        convert: bool
            If false, don't convert attribute values not natively converted by the
            container format (e.g. dates)
        *args
            Collect and ignore additional positional arguments so the reader can
            be swapped with other readers that might take additional arguments
        **kwargs
            See `args`
        """

        self.writer = writer
        self.force_message = force_message
        self.convert = convert
        self.keep_fields = keep_fields
        self.throw_exceptions = throw_exceptions

    @classmethod
    def open(cls, f, format=None, format_options={}, *args, **kwargs):
        """
        Write the GPSD format to a file using one of the registered container formats.

        Parameters
        ----------
        f : file
            An open file object
        format: 'json' | 'msgpack'
            The name of a container format registered with ContainerFormat
        format_options: dict
            Dictionary with optional arguments for the container format writer
        Any additional arguments are passed directly on to __init__.

        """

        return cls(
            ContainerFormat.open(f, format=format, usage='writer'),
            *args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def closed(self):
        """
        Indicates whether or not the file object being read from is closed

        Returns
        -------
        bool
        """

        return self.writer.closed

    def writeheader(self):
        """
        Write a file header if one is needed by the container format
        """

        if hasattr(self.writer, 'writeheader'):
            self.writer.writeheader()

    def writerow(self, row):
        """
        Write a line to the output file minus any keys that do not appear in
        the ``fieldnames`` property.

        Returns
        -------
        None
        """

        if not self.keep_fields and 'type' in row:
            row = {field: val for field, val in six.iteritems(row)
                   if field in schema.get_default_msg(row['type'])}

        if self.convert:
            if self.force_message:
                row = schema.row2message(row, keep_fields=self.keep_fields)
            row = schema.export_msg(row, throw_exceptions=self.throw_exceptions)

        self.writer.writerow(row)

    def writerows(self, rows):
        """
        Calls the ``writerow()`` method on a list of rows

        Returns
        -------
        None
        """

        for row in rows:
            self.writerow(row)

    def close(self):
        """
        Close the open file object the writer is editing

        Returns
        -------
        None
        """

        self.writer.close()

class _FileContainer(object):
    def __init__(self, f):
        self.f = f

    @property
    def name(self):
        return getattr(self.f, 'name', 'Unknown')

    @property
    def closed(self):
        return self.f.closed

    def close(self):
        self.f.close()

class _FileReader(_FileContainer):
    def __iter__(self):
        return self

class _JSONReader(_FileContainer):
    def next(self):
        line = self.f.next()
        try:
            return json.loads(line.strip())
        except Exception as e:
            return {"__invalid__": {"__content__": line}}
class _JSONWriter(_FileContainer):
    def writerow(self, row):
        json.dump(row, self.f)
        self.f.write("\n")
ContainerFormat.register("json", _JSONReader, _JSONWriter)


class _MsgPackReader(_FileReader):
    def __init__(self, *arg, **kw):
        super(_MsgPackReader, self).__init__(*arg, **kw)
        self.reader = msgpack.Unpacker(self.f)
    def next(self):
        return self.reader.next()
class _MsgPackWriter(_FileContainer):
    def writerow(self, row):
        msgpack.dump(row, self.f)
ContainerFormat.register("msg", _MsgPackReader, _MsgPackWriter)
ContainerFormat.register("msgpack", _MsgPackReader, _MsgPackWriter)


def as_geojson(iterator, x_field='longitude', y_field='latitude'):

    """
    Convert GPSD to GeoJSON Points on the fly.

    Parameters
    ----------
    iterator : iterable object
        An iterable object that produces one GPSD message per iteration.
    x_field : str, optional
        Field containing longitude.  Will be converted to a GeoJSON point and
        removed from the output.
    y_field : str, optional
        Field containing latitude.  Will be converted to a GeoJSON point and
        removed from the output.
    """

    for idx, row in enumerate(iterator):
        o = {
            'id': idx,
            'type': 'Feature',
            'properties': {k: v for k, v in row.items() if k not in (x_field, y_field)},
            'geometry': {
                'type': 'Point',
                'coordinates': (row[x_field], row[y_field])
            }
        }
        del o[x_field]
        del o[y_field]
        yield o


def from_geojson(iterator, x_field='longitude', y_field='latitude'):

    """
    Convert GeoJSON Points to GPSD on the fly.

    Parameters
    ----------
    iterator : iterable object
        An iterable object that produces one GeoJSON Point message per iteration.
        Note that
    x_field : str, optional
        Write longitude to this field - will be overwritten if it already exists.
    y_field : str, optional
        Write latitude to this field - will be overwritten if it already exists.

    Raises
    ------
    TypeError
        Input object isn't a GeoJSON Point.

    Yields
    ------
    dict
        GPSD message.
    """

    for feature in iterator:

        if feature['geometry']['type'] != 'Point':
            raise TypeError("Input object is not a GeoJSON point: %s" % feature)

        point = feature['geometry']['coordinates']
        o = feature['properties']
        o[x_field] = point[0]
        o[y_field] = point[1]

        yield o
