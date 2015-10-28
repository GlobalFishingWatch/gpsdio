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


def test_filter(types_msg_gz_path, types_json_gz_path):

    # Pass all through unaltered
    with gpsdio.open(types_msg_gz_path) as actual, gpsdio.open(types_msg_gz_path) as expected:
        for a, e in zip(gpsdio.ops.filter("isinstance(mmsi, int)", actual), expected):
            assert a == e

    # Extract only types 1, 2, and 3
    passed = []
    with gpsdio.open(types_msg_gz_path) as stream:
        for msg in gpsdio.ops.filter("type in (1,2,3)", stream):
            passed.append(msg)
            assert msg['type'] in (1, 2, 3)
    assert len(passed) >= 3

    # Filter out everything
    with gpsdio.open(types_msg_gz_path) as stream:
        for msg in gpsdio.ops.filter(("type is 5", "mmsi is -1000"), stream):
            assert False, "Above loop should not have executed because the filter should " \
                          "not have yielded anything."

    # Multiple expressions
    passed = []
    with gpsdio.open(types_msg_gz_path) as stream:
        for msg in gpsdio.ops.filter(
                ("status == 'Under way using engine'", "mmsi is 366268061"), stream):
            passed.append(msg)
            assert msg['mmsi'] is 366268061

    # Reference the entire message
    passed = []
    with gpsdio.open(types_json_gz_path) as stream:
        for msg in gpsdio.ops.filter(("isinstance(msg, dict)", "'lat' in msg"), stream):
            passed.append(msg)
            assert 'lat' in msg
    assert len(passed) >= 9

    # Multiple complex filters
    criteria = ("turn is 0 and second is 0", "mmsi == 366268061", "'lat' in msg")
    with gpsdio.open(types_json_gz_path) as stream:
        passed = [m for m in gpsdio.ops.filter(criteria, stream)]
        assert len(passed) >= 1
