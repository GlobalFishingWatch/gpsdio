"""
Unittests for features that have been deprecated or moved.
"""


import pytest

import gpsdio
import gpsdio.schema
import gpsdio.drivers


def test_filter_old_location(types_msg_gz_path, types_json_gz_path):

    # Pass all through unaltered
    with gpsdio.open(types_msg_gz_path) as actual, gpsdio.open(types_msg_gz_path) as expected:
        for a, e in zip(gpsdio.filter("isinstance(mmsi, int)", actual), expected):
            assert a == e

    # Extract only types 1, 2, and 3
    passed = []
    with gpsdio.open(types_msg_gz_path) as stream:
        for msg in gpsdio.filter("type in (1,2,3)", stream):
            passed.append(msg)
            assert msg['type'] in (1, 2, 3)
    assert len(passed) >= 3

    # Filter out everything
    with gpsdio.open(types_msg_gz_path) as stream:
        for msg in gpsdio.filter(("type is 5", "mmsi is -1000"), stream):
            assert False, "Above loop should not have executed because the filter should " \
                          "not have yielded anything."

    # Multiple expressions
    passed = []
    with gpsdio.open(types_msg_gz_path) as stream:
        for msg in gpsdio.filter(
                ("status == 'Under way using engine'", "mmsi is 366268061"), stream):
            passed.append(msg)
            assert msg['mmsi'] is 366268061

    # Reference the entire message
    passed = []
    with gpsdio.open(types_json_gz_path) as stream:
        for msg in gpsdio.filter(("isinstance(msg, dict)", "'lat' in msg"), stream):
            passed.append(msg)
            assert 'lat' in msg
    assert len(passed) >= 9

    # Multiple complex filters
    criteria = ("turn is 0 and second is 0", "mmsi == 366268061", "'lat' in msg")
    with gpsdio.open(types_json_gz_path) as stream:
        passed = [m for m in gpsdio.filter(criteria, stream)]
        assert len(passed) >= 1


def test_warnings():
    with pytest.warns(FutureWarning):
        gpsdio.sort(None, None)
    with pytest.warns(FutureWarning):
        gpsdio.filter(None, None)
