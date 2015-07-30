"""
gpsdio env
"""


import doctest
import logging

import click

import gpsdio
import gpsdio.drivers
from gpsdio.drivers import registered_compression
from gpsdio.drivers import registered_drivers


@click.command()
@click.option(
    '--drivers', 'item', flag_value='drivers',
    help="List of registered drivers and their I/O modes."
)
@click.option(
    '--compression', 'item', flag_value='compression',
    help='List of registered compression drivers and their I/O modes.'
)
@click.option(
    '--driver-help', 'get_help', metavar='NAME',
    help="Print a driver's documentation."
)
@click.option(
    '--compression-help', 'get_help', metavar='NAME',
    help="Print a compression driver's documentation."
)
@click.pass_context
def env(ctx, item, get_help):

    """
    Information about the gpsdio environment.
    """

    logger = logging.getLogger('gpsdio-cli-env')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting env')

    if item == 'drivers':
        for name, driver in gpsdio.drivers._BaseDriver.by_name.items():
            click.echo("%s - %s" % (name, driver.io_modes))
    elif item == 'compression':
        for name, driver in gpsdio.drivers._BaseCompressionDriver.by_name.items():
            click.echo("%s - %s" % (name, driver.io_modes))
    elif get_help:
        if get_help in registered_drivers:
            click.echo(registered_drivers[get_help].__doc__)
        elif get_help in registered_compression:
            click.echo(registered_compression[get_help].__doc__)
        else:
            click.BadParameter("Unrecognized driver or compression: {}".format(get_help))
    else:
        raise click.BadParameter('A flag is required.')
