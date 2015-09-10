"""
Message modification operations.
"""


import copy

import gpsdio.schema


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

    allowed_keys = gpsdio.schema.CURRENT.keys()

    for msg in stream:

        # Copy the input message to make sure we don't modify the dicts outside
        # this scope.  Valid fields are removed from this `invalid` dict, which
        # just leaves us with the invalid keys
        invalid = copy.deepcopy(msg)

        m = {
            k: invalid.pop(k) for k in invalid.keys() if k in allowed_keys}

        if keep_invalid and invalid:
            m[invalid_key] = invalid

        yield m
