"""
Unittests for gpsdio env
"""


import json

import gpsdio
import gpsdio.base
import gpsdio.cli
import gpsdio.cli.env
import gpsdio.cli.main
import gpsdio.drivers


def test_drivers(runner):
    result = runner.invoke(gpsdio.cli.main.main_group, [
        'env', 'drivers'
    ])
    assert result.exit_code is 0
    for name in gpsdio.drivers._DRIVERS.keys():
        assert name in result.output


def test_driver_help(runner):
    result = runner.invoke(gpsdio.cli.main.main_group, [
        'env', 'drivers', 'NewlineJSON'
    ])
    assert result.exit_code is 0
    assert result.output.strip() == gpsdio.drivers.NewlineJSON.__doc__.strip()


def test_compression(runner):
    result = runner.invoke(gpsdio.cli.main.main_group, [
        'env', 'compression'
    ])
    assert result.exit_code is 0
    for name in gpsdio.drivers._COMPRESSION.keys():
        assert name in result.output


def test_compression_help(runner):
    result = runner.invoke(gpsdio.cli.main.main_group, [
        'env', 'compression', 'GZIP'
    ])
    assert result.exit_code is 0
    assert result.output.strip() == gpsdio.drivers.GZIP.__doc__.strip()


def test_schema(runner):
    result = runner.invoke(gpsdio.cli.main.main_group, [
        'env', 'fields'
    ])
    assert result.exit_code == 0
    expected = json.dumps(
        gpsdio.cli.env._scrub_dict(gpsdio._schema._FIELDS), indent=4, sort_keys=True)
    assert result.output.strip() == expected.strip()


def test_schema_field(runner):
    result = runner.invoke(gpsdio.cli.main.main_group, [
        'env', 'fields', '--indent', 'None', 'mmsi'
    ])
    assert result.exit_code == 0
    expected = json.dumps(
        gpsdio.cli.env._scrub_dict(gpsdio._schema._FIELDS['mmsi']), sort_keys=True)
    assert result.output.strip() == expected.strip()
