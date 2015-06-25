import json

from click.testing import CliRunner
import six

import gpsdio.cli.main


def test_indented_is_default():
    default = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        'sample-data/types.json'
    ])
    assert default.exit_code == 0
    assert len(default.output.splitlines()) > 1

    indented = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        '--indent', '4',
        'sample-data/types.json'
    ])
    assert indented.exit_code == 0
    assert len(indented.output.splitlines()) > 1

    assert default.output == indented.output


def test_full_info():
    result = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        '--with-mmsi-hist',
        '--with-type-hist',
        'sample-data/types.msg.gz'
    ])
    assert result.exit_code == 0

    stats = json.loads(result.output)

    assert not stats['sorted']
    assert stats['bounds'] == [-123.0387, 0, 0, 49.1487]
    assert stats['count'] >= 20
    assert gpsdio.schema.str2datetime(stats['min_timestamp']) \
        < gpsdio.schema.str2datetime(stats['max_timestamp'])
    assert len(stats['type_histogram']) >= 20
    assert len(stats['mmsi_histogram']) >= 20


def test_type_and_mmsi_hist_implicit():
    # Make sure that histograms are automatically enabled if they are the
    # only requested member
    for flag in ('--type-hist', '--mmsi-hist'):
        result = CliRunner().invoke(gpsdio.cli.main.main_group, [
            'info',
            flag,
            'sample-data/types.msg.gz'
        ])
        assert result.exit_code == 0
        decoded = json.loads(result.output)
        assert isinstance(decoded, dict)
        assert len(decoded) >= 20
        for k, v in decoded.iteritems():
            assert isinstance(k, six.string_types)
            assert isinstance(v, int)
            assert k.isdigit()


def test_single_members():
    full = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        '--with-mmsi-hist',
        '--with-type-hist',
        'sample-data/types.msg.gz'
    ])
    assert full.exit_code == 0

    flag_member = {
        '--bounds': 'bounds',
        '--count': 'count',
        '--mmsi-hist': 'mmsi_histogram',
        '--type-hist': 'type_histogram',
        '--min-timestamp': 'min_timestamp',
        '--max-timestamp': 'max_timestamp',
        '--sorted': 'sorted',
        '--num-unique-mmsi': 'num_unique_mmsi',
        '--num-unique-type': 'num_unique_type'
    }
    for flag, member in flag_member.items():
        single = CliRunner().invoke(gpsdio.cli.main.main_group, [
            'info',
            'sample-data/types.json',
            flag
        ])
        assert single.exit_code == 0
        val = json.loads(full.output)[member]
        if isinstance(val, (dict, bool)):
            assert val == json.loads(single.output)
        elif isinstance(val, (list, tuple)):
            assert " ".join(map(str, val))
        else:
            assert str(val).strip() == single.output.strip()
