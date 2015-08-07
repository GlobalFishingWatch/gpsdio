"""
Unittests for gpsdio env
"""


import json

from click.testing import CliRunner

import gpsdio
import gpsdio.base
import gpsdio.cli
import gpsdio.cli.env
import gpsdio.drivers


def test_drivers():
    result = CliRunner().invoke(gpsdio.cli.main_group, [
        'env', 'drivers'
    ])
    assert result.exit_code is 0
    for name in gpsdio.drivers.registered_drivers.keys():
        assert name in result.output


def test_driver_help():
    result = CliRunner().invoke(gpsdio.cli.main_group, [
        'env', 'drivers', 'NewlineJSON'
    ])
    assert result.exit_code is 0
    assert result.output.strip() == gpsdio.drivers.NewlineJSON.__doc__.strip()


def test_compression():
    result = CliRunner().invoke(gpsdio.cli.main_group, [
        'env', 'compression'
    ])
    print(result.output)
    assert result.exit_code is 0
    for name in gpsdio.drivers.registered_compression.keys():
        assert name in result.output


def test_compression_help():
    result = CliRunner().invoke(gpsdio.cli.main_group, [
        'env', 'compression', 'GZIP'
    ])
    assert result.exit_code is 0
    assert result.output.strip() == gpsdio.drivers.GZIP.__doc__.strip()


def test_schema():
    result = CliRunner().invoke(gpsdio.cli.main_group, [
        'env', 'schema'
    ])
    assert result.exit_code == 0
    expected = json.dumps(
        gpsdio.cli.env._scrub_dict(gpsdio.schema.CURRENT), indent=4, sort_keys=True)
    assert result.output.strip() == expected.strip()


def test_schema_field():
    result = CliRunner().invoke(gpsdio.cli.main_group, [
        'env', 'schema', '--indent', 'None', 'mmsi'
    ])
    assert result.exit_code == 0
    expected = json.dumps(
        gpsdio.cli.env._scrub_dict(gpsdio.schema.CURRENT['mmsi']), sort_keys=True)
    assert result.output.strip() == expected.strip()
