"""
Read and write the GPSD format. The API mimics
that of csv.DictReader/DictWriter and uses gpsd_format.schema to get schema details
"""


try:
    import msgpack
except ImportError:
    msgpack = None
import json

import gpsd_format.schema


__all__ = ['GPSDReader', 'GPSDWriter']


def json_reader(f):
    for line in f:
        try:
            yield json.loads(line.strip())
        except Exception, e:
            yield {"__invalid__": {"__content__": line}}


class _MsgPackWriter(object):
    def __init__(self, f):
        self.f = f

    def writerow(self, row):
        msgpack.dump(row, self.f)


class _JSONWriter(object):
    def __init__(self, f):
        self.f = f

    def writerow(self, row):
        json.dump(row, self.f)
        self.f.write("\n")


class GPSDReader(object):
    container_formats = {
        'msg': msgpack.Unpacker,
        'msgpack': msgpack.Unpacker,
        'json': json_reader
        }

    def __init__(self, f, force_message=False, keep_fields=True, throw_exceptions=True, convert=True, container=None,
                 *args, **kwargs):
        """
        Read the GPSD format. The API mimics that of
        csv.DictReader.

        Parameters
        ----------
        f : file
            An open file object
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
        container: function
            A function that iterates over a file handle producing a messages (dictionaries).
            Default depends on the file extension in f.name
        *args
            Collect and ignore additional positional arguments so the reader can
            be swapped with other readers that might take additional arguments
        **kwargs
            See `args`
        """

        self.f = f
        if container is None:
            if hasattr(f, 'name'):
                container = self.container_formats.get(f.name.rsplit(".", 1)[1])
            else:
                container = self.container_formats['json']
        self.container = container
        self.reader = self.container(self.f)
        self.convert = convert
        self.force_message = force_message
        self.keep_fields = keep_fields
        self.throw_exceptions = throw_exceptions

    def __iter__(self):
        return self

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

        return self.f.closed

    def next(self):
        """
        Get the next non-empty line in the file

        Returns
        -------
        dict
        """

        line = None
        try:
            loaded = line = self.reader.next()
            if self.convert:
                loaded = gpsd_format.schema.import_row(line, throw_exceptions=self.throw_exceptions)
                if self.force_message:
                    loaded = gpsd_format.schema.row2message(loaded, keep_fields=self.keep_fields)
            return loaded
        except StopIteration:
            raise
        except Exception, e:
            if self.throw_exceptions:
                raise Exception("%s: %s: %s" % (self.f.name, type(e), e))
            return {"__invalid__": {"__content__": line}}

    def close(self):
        """
        Close the file object being read from

        Returns
        -------
        None
        """

        self.f.close()


class GPSDWriter(object):
    container_formats = {
        'msg': _MsgPackWriter,
        'msgpack':  _MsgPackWriter,
        'json': _JSONWriter
        }

    def __init__(self, f, force_message=False, keep_fields=True, throw_exceptions=True, convert=True, container=None,
                 *args, **kwargs):
        """
        Write the GPSD format. The API mimics that of
        csv.DictWriter.

        Parameters
        ----------
        f : file
            An open file object equivalent to f = open(path, mode)
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
        container: class
            A class that takes a file handle and provides a writerow() function
            Default depends on the file extension in f.name
        *args
            Collect and ignore additional positional arguments so the reader can
            be swapped with other readers that might take additional arguments
        **kwargs
            See `args`
        """

        self.f = f
        if container is None:
            if hasattr(f, 'name'):
                container = self.container_formats.get(f.name.rsplit(".", 1)[1])
            else:
                container = self.container_formats['json']
        self.container = container
        self.writer = self.container(self.f)
        self.force_message = force_message
        self.convert = convert
        self.keep_fields = keep_fields
        self.throw_exceptions = throw_exceptions

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

        return self.f.closed

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
            row = {field: val for field, val in row.iteritems()
                   if field in gpsd_format.schema.get_message_default(row['type'])}

        if self.convert:
            if self.force_message:
                row = gpsd_format.schema.row2message(row, keep_fields=self.keep_fields)
            row = gpsd_format.schema.export_row(row, throw_exceptions=self.throw_exceptions)

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

        self.f.close()
