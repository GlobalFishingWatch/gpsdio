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
                print(e)
                print(a)
                msg_almost_equal(e, a)


def test_cat_geojson(types_msg_gz_path):
    result = subprocess.check_output(
        ['gpsdio', 'cat', '--geojson', types_msg_gz_path]).decode('utf-8')
    actual = (json.loads(l) for l in result.splitlines())
    with gpsdio.open(types_msg_gz_path) as expected:
        for e, a in zip(gpsdio.ops.geojson(expected), actual):
            assert a['type'] == 'Feature'
            assert a['geometry']['type'] == 'Point'
            assert a == a


def test_cat_geojson_non_posit(types_json_path, tmpdir):
    # pth = str(tmpdir.mkdir('test').join('test_cat_geojson_non_posit.json'))
    pth = 'AH.json'
    with gpsdio.open(types_json_path) as src, gpsdio.open(pth, 'w') as dst:
        # Write a single type 1 and a single type 5 - one posit and one non-posit
        messages = {msg['type']: msg for msg in src}
        dst.write(messages[1])
        dst.write(messages[5])
    result = subprocess.check_output(['gpsdio', 'cat', '--geojson', pth]).decode('utf-8')
    geojson = [json.loads(l) for l in result.splitlines()]
    assert len(geojson) is 1
    assert geojson[0]['properties']['type'] is 1
