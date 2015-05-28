"""
Main click group for the gpsdio CLI.  This must be isolated from the
other commands.
"""


import itertools
from pkg_resources import iter_entry_points

import click
import cligj.plugins

import gpsdio.drivers


@cligj.plugins.group(plugins=(
    p for p in itertools.chain(*(iter_entry_points('gpsdio.gpsdio_commands'),
                                 iter_entry_points('gpsdio.gpsdio_plugins')))))
@click.option(
    '--input-driver', metavar='NAME', default=None,
    help='Specify the input driver.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseDriver.by_name.keys()))
)
@click.option(
    '--output-driver', metavar='NAME', default=None,
    help='Specify the output driver.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseDriver.by_name.keys()))
)
@click.option(
    '--input-compression', metavar='NAME', default=None,
    help='Input compression format.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseCompressionDriver.by_name.keys()))
)
@click.option(
    '--output-compression', metavar='NAME', default=None,
    help='Output compression format.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseCompressionDriver.by_name.keys()))
)
@click.pass_context
def main_group(ctx, input_driver, output_driver, input_compression, output_compression):
    """
    A collection of tools for working with the GPSD JSON format (or the same format in a msgpack container)
    """

    ctx.obj = {
        'i_driver': input_driver,
        'o_driver': output_driver,
        'i_compression': input_compression,
        'o_compression': output_compression
    }
