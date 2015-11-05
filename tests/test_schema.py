"""
Unittsts for gpsdio.schema and gpsdio._schema
"""


import gpsdio.schema


def test_ensure_access():

    """
    Some objects are defined in `_schema.py` that need to be available through
    the public API in `schema.py`.
    """

    assert gpsdio.schema.datetime2str
    assert gpsdio.schema.str2datetime
    assert gpsdio.schema.DATETIME_FORMAT
