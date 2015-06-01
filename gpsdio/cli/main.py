"""
Main click group for the gpsdio CLI.  This must be isolated from the
other commands.
"""


import itertools
import logging
from pkg_resources import iter_entry_points
import sys

import click
import cligj.plugins

import gpsdio
import gpsdio.drivers


@cligj.plugins.group(plugins=(
    ep for ep in itertools.chain(*(iter_entry_points('gpsdio.gpsdio_commands'),
                                 iter_entry_points('gpsdio.gpsdio_plugins')))))
@click.version_option(gpsdio.__version__)
@click.option('--verbose', '-v', count=True, help="Increase verbosity.")
@click.option('--quiet', '-q', count=True, help="Decrease verbosity.")
@click.option(
    '--i-drv', metavar='NAME', default=None,
    help='Specify the input driver.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseDriver.by_name.keys()))
)
@click.option(
    '--o-drv', metavar='NAME', default=None,
    help='Specify the output driver.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseDriver.by_name.keys()))
)
@click.option(
    '--i-cmp', metavar='NAME', default=None,
    help='Input compression format.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseCompressionDriver.by_name.keys()))
)
@click.option(
    '--o-cmp', metavar='NAME', default=None,
    help='Output compression format.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseCompressionDriver.by_name.keys()))
)
@click.pass_context
def main_group(ctx, i_drv, o_drv, i_cmp, o_cmp, verbose, quiet):
    """
    A collection of tools for working with the GPSD JSON format (or the same format in a msgpack container)
    """

    verbosity = max(10, 30 - 10 * verbose) - quiet
    logging.basicConfig(stream=sys.stderr, level=verbosity)

    ctx.obj = {
        'i_drv': i_drv,
        'o_drv': o_drv,
        'i_cmp': i_cmp,
        'o_cmp': o_cmp,
        'verbosity': verbosity
    }
