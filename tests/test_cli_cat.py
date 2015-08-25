"""
Unittests for gpsdio cat
"""


from click.testing import CliRunner
import newlinejson as nlj
import pytest

import gpsdio
import gpsdio.cli.main
from sample_files import TYPES_MSG_GZ_FILE



@pytest.mark.skipif(True, reason="Click's CliRunner() class crashes on this test because "
                                 "gpsdio is closing sys.stdout and CliRunner() expects to "
                                 "do that itself.  Not sure what the work-around is.")
def test_cat():
    result = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'cat',
        TYPES_MSG_GZ_FILE
    ])
    assert result.exit_code is 0
    with gpsdio.open(TYPES_MSG_GZ_FILE) as expected:
        for expected, actual in zip(expected, nlj.loads(result.output)):
            assert expected == actual
