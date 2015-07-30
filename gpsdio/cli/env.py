"""
gpsdio env
"""


import logging

import click

import gpsdio
import gpsdio.drivers


@click.command()
@click.option(
    '--drivers', 'item', flag_value='drivers',
    help="List of registered drivers and their I/O modes."
)
@click.option(
    '--compression', 'item', flag_value='compression',
    help='List of registered compression drivers and their I/O modes.'
)
@click.pass_context
def env(ctx, item):

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
    else:
        raise click.BadParameter('A flag is required.')
