"""
Unittests for gpsdio insp
"""


from gpsdio.cli.main import main_group


def test_all(runner, types_json_path):
    result = runner.invoke(main_group, [
        'insp', types_json_path
    ])
    assert result.exit_code is 0
