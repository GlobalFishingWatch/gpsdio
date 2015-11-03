"""
Schema definitions and functions to transform rows
"""


import datetime
import logging

import six

from gpsdio._schema import _FIELDS
from gpsdio._schema import _FIELDS_BY_TYPE


logger = logging.getLogger('gpsdio')


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def build_schema(fields_by_type=_FIELDS_BY_TYPE, fields=_FIELDS):
    out = {}
    for mtype, mfields in six.iteritems(fields_by_type):
        definition = {}
        for fld in mfields:
            name = fields[fld].get('sub_name', fld)
            definition[name] = fields[name]
        out[mtype] = definition
    return out


def build_validator(schema):
    out = {}
    for mtype, fields in six.iteritems(schema):
        out[mtype] = {k: v['validate'] for k, v in six.iteritems(fields)}
    return out


def datetime2str(datetime_obj):

    """
    Convert a datetime object to a normalized Benthos timestamp
    Parameters
    ----------
    datetime_obj : datetime.datetime
        A loaded datetime object
    """

    return datetime_obj.strftime(DATETIME_FORMAT)


def str2datetime(string):
    """
    Convert a normalized Benthos timestamp to a datetime object
    Parameters
    ----------
    string : str
        String to convert
    """

    ms = string[20:-1]
    ms += "000000"[:6 - len(ms)]
    return datetime.datetime(
        int(string[:4]),
        int(string[5:7]),
        int(string[8:10]),
        int(string[11:13]),
        int(string[14:16]),
        int(string[17:19]),
        int(ms))