import json

from click.testing import CliRunner
import six

import gpsdio.cli.main


def test_indented_is_default(types_json_path):
    default = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        types_json_path
    ])
    assert default.exit_code == 0
    assert len(default.output.splitlines()) > 1

    indented = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        '--indent', '4',
        types_json_path
    ])
    assert indented.exit_code == 0
    assert len(indented.output.splitlines()) > 1

    assert default.output == indented.output


def test_full_info(types_msg_gz_path):
    result = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        '--with-all',
        types_msg_gz_path
    ])
    assert result.exit_code == 0

    stats = json.loads(result.output)

    # assert not stats['sorted']
    assert stats['bounds'] == [
        -90.54833221435547, -101.54704284667969, 200.23167419433594, 91.0]
    assert stats['count'] >= 20

    # assert gpsdio.schema.str2datetime(stats['min_timestamp']) \
    #     < gpsdio.schema.str2datetime(stats['max_timestamp'])

    assert len(stats['type_histogram']) >= 20
    assert len(stats['mmsi_histogram']) >= 20
    assert len(stats['field_histogram']) >= 20

    assert stats['num_unique_mmsi'] >= 20
    assert stats['num_unique_field'] >= 20
    assert stats['num_unique_type'] >= 20


def test_implicit_histograms(types_msg_gz_path):
    # Make sure that histograms are automatically enabled if they are the
    # only requested member
    for flag in ('--type-hist', '--mmsi-hist', '--field-hist'):
        result = CliRunner().invoke(gpsdio.cli.main.main_group, [
            'info',
            flag,
            types_msg_gz_path
        ])
        assert result.exit_code == 0

        decoded = json.loads(result.output)

        assert isinstance(decoded, dict)
        assert len(decoded) >= 20

        for k, v in six.iteritems(decoded):
            assert isinstance(k, six.string_types)
            assert isinstance(v, int)
            if 'field' not in flag:
                assert k.isdigit()


def test_single_members(types_msg_gz_path, types_json_path):
    full = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        '--with-all',
        types_msg_gz_path
    ])
    assert full.exit_code == 0

    flag_member = {
        '--bounds': 'bounds',
        '--count': 'count',
        '--mmsi-hist': 'mmsi_histogram',
        '--type-hist': 'type_histogram',
        '--field-hist': 'field_histogram',
        # '--min-timestamp': 'min_timestamp',
        # '--max-timestamp': 'max_timestamp',
        # '--sorted': 'sorted',
        '--num-unique-mmsi': 'num_unique_mmsi',
        '--num-unique-type': 'num_unique_type'
    }
    for flag, member in flag_member.items():
        single = CliRunner().invoke(gpsdio.cli.main.main_group, [
            'info',
            types_json_path,
            flag
        ])
        assert single.exit_code == 0

        val = json.loads(full.output)[member]

        if isinstance(val, (dict, bool)):
            assert val == json.loads(single.output)


def test_with_all(types_msg_gz_path):
    result = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        '--with-all',
        types_msg_gz_path
    ])
    assert result.exit_code == 0

    actual = list(map(six.text_type, sorted(json.loads(result.output).keys())))
    expected = list(map(six.text_type, sorted(
        ['bounds', 'count', 'field_histogram', 'mmsi_histogram',
         'num_unique_mmsi', 'type_histogram', 'num_unique_type', 'num_unique_field'])))
    # expected = list(map(six.text_type, sorted(
    #     ['bounds', 'count', 'field_histogram', 'mmsi_histogram',
    #      'num_unique_mmsi', 'type_histogram', 'max_timestamp',
    #      'min_timestamp', 'num_unique_type', 'sorted', 'num_unique_field'])))

    assert actual == expected
