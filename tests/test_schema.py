"""
Unittsts for gpsdio.schema and gpsdio._schema
"""


import datetime

import pytest

from gpsdio import schema


def test_datetime2str():
    dt = datetime.datetime.now()
    assert schema.datetime2str(dt) == dt.strftime(schema.DATETIME_FORMAT)


def test_str2datetime():
    pass


def test_DateTime():

    v = schema.DateTime()
    dt = datetime.datetime.now()

    # with datetime
    assert dt == v(dt)

    # with string
    assert dt == v(dt.strftime(schema.DATETIME_FORMAT))

    # Bad value w/ coerce
    with pytest.raises(schema.Invalid):
        v(None)

    # Bad value no coerce
    with pytest.raises(schema.Invalid):
        schema.DateTime(coerce=False)(None)


def test_IntRange():

    # Two negatives
    assert schema.IntRange(-3, -1)(-2) is -2

    # Two positives
    assert schema.IntRange(1, 3)(2) is 2

    # Negative positive
    assert schema.IntRange(-1, 1)(0) is 0

    # All 0's
    assert schema.IntRange(0, 0)(0) is 0

    # From string
    assert schema.IntRange(1, 3)("2") is 2

    # Min only
    assert schema.IntRange(0)(2) is 2

    # Max only
    assert schema.IntRange(minimum=None, maximum=2)(1) is 1

    # No min max
    with pytest.raises(ValueError):
        schema.IntRange()

    # String no coerce
    with pytest.raises(schema.Invalid):
        schema.IntRange(1, 3, coerce=False)("2")

    # Coerce bad value
    with pytest.raises(schema.Invalid):
        schema.IntRange(1, 3)('words')

    # Value below min
    with pytest.raises(schema.Invalid):
        schema.IntRange(0)(-1)

    # Value above max
    with pytest.raises(schema.Invalid):
        schema.IntRange(0, 1)(2)


def test_FloatRange():

    # No min or max
    with pytest.raises(schema.Invalid):
        schema.FloatRange()

    # With min and max
    assert schema.FloatRange(1.2, 3.4)(2.2) == 2.2

    # With string
    assert schema.FloatRange(1.2)("3.4") == 3.4

    # Min only
    assert schema.FloatRange(1.23)(2.2) == 2.2

    # max only
    assert schema.FloatRange(minimum=None, maximum=2.2)(1.1) == 1.1

    # With string no coerce
    with pytest.raises(schema.Invalid):
        schema.FloatRange(1.2, coerce=False)("3.4")

    # Value < min
    with pytest.raises(schema.Invalid):
        schema.FloatRange(1.1)(-1.1)

    # Value > max
    with pytest.raises(schema.Invalid):
        schema.FloatRange(minimum=None, maximum=2.2)(3.3)

    # Coerce bad string
    with pytest.raises(schema.Invalid):
        schema.FloatRange(1.1, 2,2)('uh oh')


def test_IntIn():

    # Value in list
    assert schema.IntIn([0, 1])(1) is 1

    # Coerce string
    assert schema.IntIn([0, 1])("1") is 1

    # Value not in list
    with pytest.raises(schema.Invalid):
        schema.IntIn([])(1)

    # Bad string
    with pytest.raises(schema.Invalid):
        schema.IntIn([0, 1])('ham')

    # No coerce bad value
    with pytest.raises(schema.Invalid):
        schema.IntIn([0, 1], coerce=False)('ahhh')


def test_Int():

    # Valid
    assert schema.Int()(1) is 1

    # Coerce
    assert schema.Int()('1') is 1

    # Coerce bad value
    with pytest.raises(schema.Invalid):
        schema.Int()('cool dog, yo')

    # No coerce wrong type
    with pytest.raises(schema.Invalid):
        schema.Int(coerce=False)('no good')
