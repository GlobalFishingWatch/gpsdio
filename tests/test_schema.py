"""
Unittsts for gpsdio.schema and gpsdio._schema
"""


import datetime

import pytest

import gpsdio.schema
from gpsdio.schema import DATETIME_FORMAT
from gpsdio.schema import DateTime


def test_ensure_public_api_access():

    """
    Some objects are defined in `_schema.py` that need to be available through
    the public API in `schema.py`.
    """

    assert gpsdio.schema.datetime2str
    assert gpsdio.schema.str2datetime
    assert gpsdio.schema.DATETIME_FORMAT


def test_DateTime():
    dt = datetime.datetime.now()

    v = DateTime()
    assert dt == v(dt)
    assert dt == v(dt.strftime(DATETIME_FORMAT))
    with pytest.raises(gpsdio.schema.Invalid):
        v(None)
