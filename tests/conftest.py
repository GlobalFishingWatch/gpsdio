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


@pytest.fixture(scope='function')
def msg_almost_equal():
    def _msg_almost_equal(m1, m2, precision=7):
        m1keys = sorted(m1.keys())
        m2keys = sorted(m2.keys())
        assert m1keys == m2keys
        for m1k, m2k in zip(m1keys, m2keys):
            m1v = m1[m1k]
            m2v = m2[m2k]
            if isinstance(m1v, float) or isinstance(m1v, float):
                assert round(m1v, precision) == round(m2v, precision)
            else:
                assert m1v == m2v
    return _msg_almost_equal
