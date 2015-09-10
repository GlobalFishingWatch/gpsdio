"""
Unittests for `gpsdio.base`
"""


import pytest

import gpsdio
import gpsdio.base


def test_wrong_mode():
    with pytest.raises(ValueError):
        with gpsdio.open('sample-data/types.json', mode='bad mode') as src:
            pass


def test_BaseDriver_open_exception():
    with pytest.raises(NotImplementedError):
        gpsdio.base.BaseDriver('sample-data/types.json')


def test_BaseCompressionDriver_open_exception():
    with pytest.raises(NotImplementedError):
        gpsdio.base.BaseCompressionDriver('sample-data/types.json.gz')
