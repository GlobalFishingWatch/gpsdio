"""
Unittests for `gpsdio.base`
"""


import pytest

import gpsdio


def test_wrong_mode():
    with pytest.raises(ValueError):
        with gpsdio.open('sample-data/types.json', mode='bad mode') as src:
            pass
