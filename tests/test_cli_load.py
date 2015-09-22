"""
Unittests for gpsdio load
"""


from click.testing import CliRunner

import gpsdio
import gpsdio.cli.main


def test_load(types_json_path, types_msg_gz_path, tmpdir, compare_msg):

    pth = str(tmpdir.mkdir('test').join('test_load'))
    with open(types_json_path) as f:
        stdin_input = f.read()

    result = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'load',
        '--o-drv', 'NewlineJSON',
        '--o-cmp', 'GZIP',
        pth

    ], input=stdin_input)

    assert result.exit_code is 0

    with gpsdio.open(types_msg_gz_path) as expected, \
            gpsdio.open(pth, driver='NewlineJSON', compression='GZIP') as actual:
        for e, a in zip(expected, actual):
            assert compare_msg(e, a)
