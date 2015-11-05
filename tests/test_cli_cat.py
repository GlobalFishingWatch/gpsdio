"""
Unittests for gpsdio cat

The `click.testing.CliRunner()` can't test commands that close stdout so we
have to use `subprocess.check_output()`
"""


import json
import subprocess

import six

import gpsdio
import gpsdio.base
import gpsdio.ops


def test_cat(types_msg_gz_path, msg_almost_equal):
    result = subprocess.check_output(['gpsdio', 'cat', types_msg_gz_path]).decode('utf-8')
    with gpsdio.open(types_msg_gz_path) as expected:
        with gpsdio.open(six.moves.StringIO(result), driver='NewlineJSON', compression=False) as actual:
            for e, a in zip(expected, actual):
                msg_almost_equal(e, a)
                # assert e == a


def test_cat_geojson(types_msg_gz_path):
    result = subprocess.check_output(
        ['gpsdio', 'cat', '--geojson', types_msg_gz_path]).decode('utf-8')
    actual = (json.loads(l) for l in result.splitlines())
    with gpsdio.open(types_msg_gz_path) as expected:
        for e, a in zip(gpsdio.ops.geojson(expected), actual):
            assert a['type'] == 'Feature'
            assert a['geometry']['type'] == 'Point'
            assert a == a
