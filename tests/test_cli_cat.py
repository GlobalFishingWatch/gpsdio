"""
Unittests for gpsdio cat
"""


from click.testing import CliRunner
import newlinejson as nlj
import pytest

import gpsdio
import gpsdio.cli.main



@pytest.mark.skipif(True, reason="Click's CliRunner() class crashes on this test because "
                                 "gpsdio is closing sys.stdout and CliRunner() expects to "
                                 "do that itself.  Not sure what the work-around is.")
def test_cat(types_msg_gz_path):
    result = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'cat',
        types_msg_gz_path
    ])
    assert result.exit_code is 0
    with gpsdio.open(types_msg_gz_path) as expected:
        for expected, actual in zip(expected, nlj.loads(result.output)):
            assert expected == actual
