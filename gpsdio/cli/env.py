"""
gpsdio env
"""


import json

import click
import six

import gpsdio
import gpsdio.schema
from gpsdio.cli import options
import gpsdio.drivers
from gpsdio.drivers import _COMPRESSION
from gpsdio.drivers import _DRIVERS


@click.group()
def env():

    """
    Information about the gpsdio environment.
    """


@env.command(name='drivers', short_help="Print registered drivers and their I/O modes.")
@click.argument('name', required=False)
def drivers_cmd(name):

    """
    To get more information about a specific driver:

    \b
        $ gpsdio env drivers ${NAME}
    """

    if name:
        try:
            click.echo(_DRIVERS[name].__doc__)
        except Exception:
            raise click.ClickException('Unrecognized driver: {}'.format(name))
    else:
        for n, driver in gpsdio.drivers._DRIVERS.items():
            click.echo("%s - %s" % (n, driver.io_modes))


@env.command(name='compression', short_help="Print compression drivers and their I/O modes.")
@click.argument('name', required=False)
def compression_cmd(name):

    """
    To get more information about a specific compression driver:

    \b
        $ gpsdio env compression ${NAME}
    """

    if name:
        try:
            click.echo(_COMPRESSION[name].__doc__)
        except Exception:
            raise click.ClickException('Unrecognized driver: {}'.format(name))
    else:
        for n, driver in gpsdio.drivers._COMPRESSION.items():
            click.echo("%s - %s" % (n, driver.io_modes))


def _scrub_val(val):
    types = (list, dict, int, float, bool, type(None)) + six.string_types
    if isinstance(val, types):
        return val
    else:
        return str(val)


def _scrub_dict(obj):

    """
    Converts non-JSON serializable objects to strings.
    """

    if isinstance(obj, dict):
        return {k: _scrub_dict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return list(map(str, obj))
    else:
        return _scrub_val(obj)


@env.command(name='fields', short_help="Information about schema fields.")
@click.argument('field', required=False)
@options.indent_opt
def fields_cmd(field, indent):

    """
    To get information about a specific field:

    \b
        $ gpsdio env schema ${FIELD}
    """

    all_fields = gpsdio.schema.merge_fields(
        gpsdio.schema._FIELDS, gpsdio.schema.FIELD_EXTENSIONS)

    if field:
        try:
            val = all_fields[field]
        except Exception:
            raise click.ClickException("Unrecognized field: {}".format(field))
    else:
        val = all_fields

    click.echo(json.dumps(_scrub_dict(val), indent=indent, sort_keys=True))


@env.command(name='types', short_help="Information about message types.")
@click.argument('msg_type', type=click.INT, required=False)
@click.option(
    '--describe', is_flag=True,
    help="Print short human readable type description.")
@options.indent_opt
def types_cmd(msg_type, indent, describe):

    """
    To get information about a specific message type:

    \b
        $ gpsdio env schema ${TYPE}
    """

    all_types = gpsdio.schema.merge_fields_by_type(
        gpsdio.schema._FIELDS_BY_TYPE, gpsdio.schema.FIELDS_BY_TYPE_EXTENSIONS)

    if msg_type is not None:
        try:
            val = all_types[msg_type]
        except Exception:
            raise click.ClickException("Unrecognized message type: {}".format(msg_type))
    else:
        val = all_types

    # Print human-readable field definition
    if describe and msg_type is None:
        raise click.ClickException("Need a message type to describe.")
    elif describe:
        click.echo(gpsdio.schema._HUMAN_TYPE_DESCRIPTION[msg_type])

    # Print some dictionary
    else:
        click.echo(json.dumps(_scrub_dict(val), indent=indent, sort_keys=True))
