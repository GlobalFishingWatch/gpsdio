"""
pytest fixtures
"""


import os

import click.testing
import pytest


@pytest.fixture(scope='function')
def types_json_path():
    return os.path.join('tests', 'data', 'types.json')


@pytest.fixture(scope='function')
def types_json_bz2_path():
    return os.path.join('tests', 'data', 'types.json.bz2')


@pytest.fixture(scope='function')
def types_json_gz_path():
    return os.path.join('tests', 'data', 'types.json.gz')


@pytest.fixture(scope='function')
def types_json_xz_path():
    return os.path.join('tests', 'data', 'types.json.xz')


@pytest.fixture(scope='function')
def types_msg_path():
    return os.path.join('tests', 'data', 'types.msg')
    

@pytest.fixture(scope='function')
def types_msg_bz2_path():
    return os.path.join('tests', 'data', 'types.msg.bz2')


@pytest.fixture(scope='function')
def types_msg_gz_path():
    return os.path.join('tests', 'data', 'types.msg.gz')


@pytest.fixture(scope='function')
def types_msg_xz_path():
    return os.path.join('tests', 'data', 'types.msg.xz')


@pytest.fixture(scope='function')
def types_nmea_path():
    return os.path.join('tests', 'data', 'types.nmea')


@pytest.fixture(scope='function')
def types_nmea_bz2_path():
    return os.path.join('tests', 'data', 'types.nmea.bz2')


@pytest.fixture(scope='function')
def types_nmea_gz_path():
    return os.path.join('tests', 'data', 'types.nmea.gz')


@pytest.fixture(scope='function')
def compare_msg():
    def _compare_msg(msg1, msg2, float_tolerance=0.00001):

        for k1, k2 in zip(sorted(list(msg1)), sorted(list(msg2))):
            v1 = msg1[k1]
            v2 = msg2[k2]
            if isinstance(v1, float) and isinstance(v2, float):
                if abs(v1 - v2) > float_tolerance:
                    return False
            else:
                if v1 != v2:
                    return False

        return True
    return _compare_msg


@pytest.fixture(scope='function')
def runner():
    return click.testing.CliRunner()
