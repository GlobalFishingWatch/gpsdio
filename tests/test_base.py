"""
Unittests for `gpsdio.base`
"""


import six
import pytest

import gpsdio
import gpsdio.base
import gpsdio.drivers


def test_wrong_mode(types_json_path):
    with pytest.raises(ValueError):
        with gpsdio.open(types_json_path, mode='bad mode') as src:
            pass


def test_GPSDIOBaseStream_schema_and_validator(types_json_path):
    with pytest.raises(ValueError), gpsdio.base.GPSDIOBaseStream(
            types_json_path,
            schema={'field': 'val'},
            _validator={'field': 'val'}) as src:
        pass


def test_BaseDriver_ctxmgr(types_json_path):
    # Test through the NewlinJSON driver because its easier
    with gpsdio.drivers.NewlineJSON() as drv:
        drv.start(types_json_path)
        assert not drv.closed
    assert drv.closed


def test_BaseDriver_attrs(tmpdir):
    pth = str(tmpdir.mkdir('test').join('test_BaseDriver_attrs.json'))
    for m in ('w', 'a', 'r'):  # w first creates file
        with gpsdio.drivers.NewlineJSON() as drv:
            drv.start(pth, mode=m)
            assert drv.mode == m

    # Make sure the required methods raise exceptions
    bd = gpsdio.base.BaseDriver()
    with pytest.raises(NotImplementedError):
        bd.io_modes
    with pytest.raises(NotImplementedError):
        bd.open(None, None)


def test_BaseCompressionDriver_attrs():
    with pytest.raises(NotImplementedError):
        gpsdio.base.BaseCompressionDriver().open(None, None)
