"""
Unittests for gpsdio cat
"""


import json
import subprocess

import gpsdio
import gpsdio.cli.main
import gpsdio.cli.cat


def test_cat(types_msg_gz_path):

    result = subprocess.check_output(['gpsdio', 'cat', types_msg_gz_path]).decode('utf-8')
    actual = (json.loads(l) for l in result.splitlines())
    with gpsdio.open(types_msg_gz_path) as expected:
        for e, a in zip(expected, actual):
            assert e == a
