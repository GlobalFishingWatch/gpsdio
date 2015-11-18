"""
Unittests for gpsdio.validate
"""


import datetime

import pytest

from gpsdio.errors import SchemaError
from gpsdio import schema
from gpsdio import validate


def test_datetime2str():
    dt = datetime.datetime.now()
    assert validate.datetime2str(dt) == dt.strftime(validate.DATETIME_FORMAT)
    assert validate.datetime2str('string') == 'string'


def test_BaseValidator():
    """Default test lets any object through."""
    v = validate.BaseValidator()
    assert v(int) is int
    assert validate.BaseValidator().coerce('ah') == 'ah'
    assert validate.BaseValidator().serialize(pytest) == pytest


def test_DateTime():

    v = schema.DateTime()
    dt = datetime.datetime.now()

    # with datetime
    assert dt == v(dt)

    # with string
    assert dt == v(dt.strftime(validate.DATETIME_FORMAT))

    # Bad value w/ coerce
    with pytest.raises(SchemaError):
        v(None)

    # Bad string
    with pytest.raises(SchemaError):
        v('bad-string')


def test_IntRange():

    # Two negatives
    assert schema.IntRange(-3, -1)(-2) is -2

    # Two positives
    assert schema.IntRange(1, 3)(2) is 2

    # Negative positive
    assert schema.IntRange(-1, 1)(0) is 0

    # All 0's
    assert schema.IntRange(0, 0)(0) is 0

    # Coerce
    assert schema.IntRange(1, 2).coerce("2") is 2

    # Min only
    assert schema.IntRange(0)(2) is 2

    # Max only
    assert schema.IntRange(maximum=2)(1) is 1

    # No min max
    # Valid test for Python but not valid for cython
    # with pytest.raises(ValueError):
    #     schema.IntRange()

    # Coerce bad value
    with pytest.raises(TypeError):
        schema.IntRange(1, 3)('words')

    # Value below min
    with pytest.raises(SchemaError):
        schema.IntRange(0)(-1)

    # Value above max
    with pytest.raises(SchemaError):
        schema.IntRange(0, 1)(2)


def test_FloatRange():

    # No min or max
    # Appropriate for Python but not Cython
    # with pytest.raises(ValueError):
    #     schema.FloatRange()

    # With min and max
    assert round(schema.FloatRange(1.2, 3.4)(2.2), 1) == 2.2

    # coerce
    assert schema.FloatRange(1.23, 2.23).coerce("3.4") == 3.4

    # Min only
    assert round(schema.FloatRange(1.23)(2.2), 1) == 2.2

    # max only
    assert round(schema.FloatRange(maximum=2.2)(1.1), 1) == 1.1

    # Value < min
    with pytest.raises(SchemaError):
        schema.FloatRange(1.1)(-1.1)

    # Value > max
    with pytest.raises(SchemaError):
        schema.FloatRange(maximum=2.2)(3.3)

    # Bad value
    with pytest.raises(TypeError):
        schema.FloatRange(1.1, 2.2)('uh oh')


def test_IntIn():

    # Value in list
    assert schema.IntIn([0, 1])(1) is 1

    # Coerce
    assert schema.IntIn([1]).coerce("1") is 1

    # Value not in list
    with pytest.raises(SchemaError):
        schema.IntIn([0])(1)

    # Bad value
    with pytest.raises(TypeError):
        schema.IntIn([0, 1])('ham')


def test_Int():

    # Valid
    assert schema.Int()(1) is 1

    # Coerce
    assert schema.Int().coerce('1') is 1

    # Coerce bad value
    with pytest.raises(TypeError):
        schema.Int()('cool dog, yo')


def test_Any():
    v = validate.Any(validate.IntIn([0]))
    with pytest.raises(SchemaError):
        v(1)


def test_All():
    v = validate.All(validate.Int())
    assert v(1) is 1
    with pytest.raises(SchemaError):
        v('string')


def test_In():
    v = validate.In(['string', 0])
    assert v('string') == 'string'
    assert v(0) is 0
    with pytest.raises(SchemaError):
        v('bad')
