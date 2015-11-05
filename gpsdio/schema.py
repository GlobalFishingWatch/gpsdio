"""
Schema definitions and functions to transform rows
"""


import logging

import six

# Do not remove datetime2str, str2datetime, or DATETIME_FORMAT
# this is their public access point
from gpsdio._schema import DATETIME_FORMAT
from gpsdio._schema import datetime2str
from gpsdio._schema import str2datetime
from gpsdio._schema import _FIELDS
from gpsdio._schema import _FIELDS_BY_TYPE


logger = logging.getLogger('gpsdio')


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
