"""
Message modification operations.
"""


import copy
import warnings

import six

import gpsdio.schema
from gpsdio.schema import export_msg


def strip_msgs(stream, keep_invalid=False, invalid_key='__invalid__'):

    """
    Remove unrecognized fields from a stream of messages.  Messages can be kept
    and moved to a specific key if desired.

    Parameters
    ----------
    stream : iter
        Iterable producing GPSd messages.
    keep_invalid : bool, optional
        Place unrecognized fields into a dictionary in `invalid_key`.
    invalid_key : str, optional
        Key to store unrecognized fields.
    """

    for msg in stream:

        # Copy the input message to make sure we don't modify the dicts outside
        # this scope.  Valid fields are removed from this `invalid` dict, which
        # just leaves us with the invalid keys
        invalid = copy.deepcopy(msg)

        m = {
            k: invalid.pop(k) for k in tuple(invalid.keys())
            if k in gpsdio.schema.fields_by_msg_type[msg['type']]}

        if keep_invalid and invalid:
            m[invalid_key] = invalid

        yield m


def geojson(stream):

    """
    **Experimental**

    Converts a stream of messages to GeoJSON features with point geometries.
    Non-positional messages are dropped.

    Currently, message type is ignored and only the lat/lon fields are used
    to determine if a message is positional.  Ultimately output messages
    will have the same schema but some internal validation work must first
    be completed.

    Parameters
    ----------
    stream : iter
        GPSd messages.

    Yields
    ------
    dict
        GeoJSON features.
    """

    warnings.warn("gpsdio.ops.geojson() is experimental.")

    for msg in stream:
        lat = msg.get('lat')
        lon = msg.get('lon')
        if lat is not None and lon is not None:
            yield {
                'type': 'Feature',
                'properties': {
                    k: v for k, v in six.iteritems(export_msg(msg))
                    if (k != 'lat' or k != 'lon')},
                'geometry': {
                    'type': 'Point',
                    'coordinates': (lon, lat)
                }
            }
