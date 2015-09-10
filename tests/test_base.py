"""
Unittests for `gpsdio.base`
"""


import pytest

import gpsdio
import gpsdio.base


def test_wrong_mode(types_json_path):
    with pytest.raises(ValueError):
        with gpsdio.open(types_json_path, mode='bad mode') as src:
            pass


def test_BaseDriver_open_exception(types_json_path):
    with pytest.raises(NotImplementedError):
        gpsdio.base.BaseDriver(types_json_path)


def test_BaseCompressionDriver_open_exception(types_json_gz_path):
    with pytest.raises(NotImplementedError):
        gpsdio.base.BaseCompressionDriver(types_json_gz_path)
