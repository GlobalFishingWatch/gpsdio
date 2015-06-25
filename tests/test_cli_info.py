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
        '--with-all',
        'sample-data/types.msg.gz'
    ])
    assert result.exit_code == 0

    stats = json.loads(result.output)

    assert not stats['sorted']
    assert stats['bounds'] == [-123.0387, 19.3668, -76.3487, 49.1487]
    assert stats['count'] >= 20

    assert gpsdio.schema.str2datetime(stats['min_timestamp']) \
        < gpsdio.schema.str2datetime(stats['max_timestamp'])

    assert len(stats['type_histogram']) >= 20
    assert len(stats['mmsi_histogram']) >= 20
    assert len(stats['field_histogram']) >= 20

    assert stats['num_unique_mmsi'] >= 20
    assert stats['num_unique_field'] >= 20
    assert stats['num_unique_type'] >= 20


def test_implicit_histograms():
    # Make sure that histograms are automatically enabled if they are the
    # only requested member
    for flag in ('--type-hist', '--mmsi-hist', '--field-hist'):
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
            if 'field' not in flag:
                assert k.isdigit()


def test_single_members():
    full = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        '--with-all',
        'sample-data/types.msg.gz'
    ])
    assert full.exit_code == 0

    flag_member = {
        '--bounds': 'bounds',
        '--count': 'count',
        '--mmsi-hist': 'mmsi_histogram',
        '--type-hist': 'type_histogram',
        '--field-hist': 'field_histogram',
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


def test_with_all():
    result = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        '--with-all',
        'sample-data/types.msg.gz'
    ])
    assert result.exit_code == 0

    actual = map(six.text_type, sorted(json.loads(result.output).keys()))
    expected = map(six.text_type, sorted(
        ['bounds', 'count', 'field_histogram', 'mmsi_histogram',
         'num_unique_mmsi', 'type_histogram', 'max_timestamp',
         'min_timestamp', 'num_unique_type', 'sorted', 'num_unique_field']))

    assert actual == expected


def test_negative_bounds(tmpdir):
    # Ensures a bug was addressed
    outfile = str(tmpdir.mkdir('out').join('outfile.msg.gz'))
    msg1 = {'lat': -21, 'lon': -20}
    msg2 = {'lat': -16, 'lon': -15}
    with gpsdio.open(outfile, 'w') as dst:
        dst.write(msg1)
        dst.write(msg2)

    result = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        outfile
    ])
    assert result.exit_code == 0

    assert json.loads(result.output)['bounds'] == [-20, -21, -15, -16]


def test_all_empty_messages(tmpdir):
    # Ensures a bug was addressed
    outfile = str(tmpdir.mkdir('out').join('outfile.msg.gz'))
    with gpsdio.open(outfile, 'w') as dst:
        dst.write({})
        dst.write({})

    result = CliRunner().invoke(gpsdio.cli.main.main_group, [
        'info',
        outfile
    ])
    assert result.exit_code == 0
