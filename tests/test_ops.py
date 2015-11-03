"""
Unittests for gpsdio.ops
"""


import gpsdio.ops


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
        msgs = list(gpsdio.ops.filter(("type is 5", "mmsi is -1000"), stream))
        assert len(msgs) is 0

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
