"""
Unittests for gpsdio env
"""


import json

import gpsdio
import gpsdio.base
import gpsdio.cli
import gpsdio.cli.env
from gpsdio.cli.main import main_group
import gpsdio.drivers
import gpsdio.schema


def test_drivers(runner):
    result = runner.invoke(main_group, [
        'env', 'drivers'
    ])
    assert result.exit_code is 0
    for name in gpsdio.drivers._DRIVERS.keys():
        assert name in result.output


def test_driver_help(runner):
    result = runner.invoke(main_group, [
        'env', 'drivers', 'NewlineJSON'
    ])
    assert result.exit_code is 0
    assert result.output.strip() == gpsdio.drivers.NewlineJSONDriver.__doc__.strip()


def test_compression(runner):
    result = runner.invoke(main_group, [
        'env', 'compression'
    ])
    assert result.exit_code is 0
    for name in gpsdio.drivers._COMPRESSION.keys():
        assert name in result.output


def test_compression_help(runner):
    result = runner.invoke(main_group, [
        'env', 'compression', 'GZIP'
    ])
    assert result.exit_code is 0
    assert result.output.strip() == gpsdio.drivers.GZIPDriver.__doc__.strip()


def test_schema(runner):
    all_fields = gpsdio.schema.merge_fields(
        gpsdio.schema._FIELDS, gpsdio.schema.FIELD_EXTENSIONS)
    result = runner.invoke(main_group, [
        'env', 'fields'
    ])
    assert result.exit_code == 0
    expected = json.dumps(
        gpsdio.cli.env._scrub_dict(all_fields), indent=4, sort_keys=True)
    assert result.output.strip() == expected.strip()


def test_schema_field(runner):
    result = runner.invoke(main_group, [
        'env', 'fields', '--indent', 'None', 'mmsi'
    ])
    assert result.exit_code == 0
    expected = json.dumps(
        gpsdio.cli.env._scrub_dict(gpsdio.schema._FIELDS['mmsi']), sort_keys=True)
    assert result.output.strip() == expected.strip()


def test_env_exceptions(runner):

    # Bad driver name
    result = runner.invoke(main_group, [
        'env', 'drivers', 'bad-name'
    ])
    assert result.exit_code != 0

    # Bad compression name
    result = runner.invoke(main_group, [
        'env', 'compression', 'bad-name'
    ])
    assert result.exit_code != 0

    # Bad field name
    result = runner.invoke(main_group, [
        'env', 'fields', 'bad-name'
    ])
    assert result.exit_code != 0

    # Bad type value
    result = runner.invoke(main_group, [
        'env', 'types', '123456789'
    ])
    assert result.exit_code != 0

    # Trying to describe a message type without specifying the type
    result = runner.invoke(main_group, [
        'env', 'types', '--describe'
    ])
    assert result.exit_code != 0


def test_types_single(runner):

    all_types = gpsdio.schema.merge_fields_by_type(
        gpsdio.schema._FIELDS_BY_TYPE, gpsdio.schema.FIELDS_BY_TYPE_EXTENSIONS)

    # List a message type's fields
    result = runner.invoke(main_group, [
        'env', 'types', '1', '--indent', 'None'
    ])
    assert result.exit_code == 0
    assert list(json.loads(result.output)) == list(all_types[1])


def test_types_describe(runner):

    # Print a type's human readable description
    result = runner.invoke(main_group, [
        'env', 'types', '1', '--describe'
    ])
    assert result.exit_code is 0
    assert result.output.strip() == gpsdio.schema._HUMAN_TYPE_DESCRIPTION[1]


def test_types_all(runner):

    # Print all fields by type
    result = runner.invoke(main_group, [
        'env', 'types',
    ])
    assert result.exit_code is 0

    # JSON Casts integer keys to string - make sure everything is directly comparable
    actual = {int(k): sorted(v) for k, v in json.loads(result.output).items()}
    expected = {int(k): sorted(v) for k, v in gpsdio.schema._FIELDS_BY_TYPE.items()}
    assert expected == actual
