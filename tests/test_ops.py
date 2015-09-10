"""
Unittests for gpsdio.ops
"""


import gpsdio.ops


def test_strip_msgs_no_keep():
    messages = [
        {'type': 3, 'mmsi': 123456789, 'imo': 1234},
        {'type': 5, 'mmsi': 987654321, 'imo': 4321, 'BAD-FIELD': 'uh-oh'},
    ]
    expected = [
        {'type': 3, 'mmsi': 123456789},
        {'type': 5, 'mmsi': 987654321, 'imo': 4321},
    ]
    for e, a in zip(expected, gpsdio.ops.strip_msgs(messages)):
        assert e == a


def test_strip_msgs_keep():
    messages = [
        {'type': 3, 'mmsi': 123456789, 'imo': 1234},
        {'type': 5, 'mmsi': 987654321, 'imo': 4321, 'BAD-FIELD': 'uh-oh'},
    ]
    expected = [
        {'type': 3, 'mmsi': 123456789, 'ikey': {'imo': 1234}},
        {'type': 5, 'mmsi': 987654321, 'imo': 4321, 'ikey': {'BAD-FIELD': 'uh-oh'}},
    ]
    strip = gpsdio.ops.strip_msgs(messages, keep_invalid=True, invalid_key='ikey')
    for e, a in zip(expected, strip):
        assert e == a
