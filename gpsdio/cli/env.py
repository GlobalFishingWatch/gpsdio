"""
gpsdio env
"""


import json

import click
import six

import gpsdio
from gpsdio.cli import options
import gpsdio.drivers
from gpsdio.drivers import registered_compression
from gpsdio.drivers import registered_drivers


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
            click.echo(registered_drivers[name].__doc__)
        except Exception:
            raise click.ClickException('Unrecognized driver: {}'.format(name))
    else:
        for n, driver in gpsdio.drivers.registered_drivers.items():
            click.echo("%s - %s" % (n, driver.io_modes))


@env.command(name='compression', short_help="Print compression drivers and their I/O modes.")
@click.argument('name', required=False)
def drivers_cmd(name):

    """
    To get more information about a specific compression driver:

    \b
        $ gpsdio env compression ${NAME}
    """

    if name:
        try:
            click.echo(registered_compression[name].__doc__)
        except Exception:
            raise click.ClickException('Unrecognized driver: {}'.format(name))
    else:
        for n, driver in gpsdio.drivers.registered_compression.items():
            click.echo("%s - %s" % (n, driver.io_modes))


def _scrub_val(val):
    types = (list, dict, int, float, bool, type(None)) + six.string_types
    if isinstance(val, types):
        return val
    else:
        return str(val)


def _scrub_dict(dictionary):

    """
    Converts non-JSON serializable objects to strings.
    """

    if isinstance(dictionary, dict):
        return {k: _scrub_dict(v) for k, v in dictionary.items()}
    elif isinstance(dictionary, (list, tuple)):
        return list(map(str, dictionary))
    else:
        return _scrub_val(dictionary)


@env.command(name='schema', short_help="Information about the schema.")
@click.argument('field', required=False)
@options.indent_opt
def schema_cmd(field, indent):

    """
    To get information about a specific field:

    \b
        $ gpsdio env schema ${FIELD}
    """

    if field:
        try:
            val = gpsdio.schema.CURRENT[field]
        except Exception:
            raise click.ClickException("Unrecognized field: {}".format(field))
    else:
        val = gpsdio.schema.CURRENT

    click.echo(json.dumps(_scrub_dict(val), indent=indent, sort_keys=True))
