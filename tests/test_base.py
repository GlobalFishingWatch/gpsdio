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
