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
import str2type.ext

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
@click.option(
    '--i-drv-opt', '--ido', 'i_drv_opts', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help='Input driver options.  JSON values are automatically decoded.',
)
@click.option(
    '--i-cmp-opt', '--ico', 'i_cmp_opts', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help='Input compression driver options.  JSON values are automatically decoded.',
)
@click.option(
    '--o-drv-opt', '--odo', 'o_drv_opts', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help='Output driver options.  JSON values are automatically decoded.',
)
@click.option(
    '--o-cmp-opt', '--oco', 'o_cmp_opts', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help='Output compression driver options.  JSON values are automatically decoded.',
)
@click.pass_context
def main_group(ctx, i_drv, o_drv, i_cmp, o_cmp, i_drv_opts, i_cmp_opts, o_drv_opts, o_cmp_opts, verbose, quiet):
    """
    A collection of tools for working with the GPSD JSON format (or the same format in a msgpack container)
    """

    verbosity = max(10, 30 - 10 * verbose) - quiet
    logging.basicConfig(stream=sys.stderr, level=verbosity)

    # A collection of objects subcommands need access to
    ctx.obj = {
        'i_drv': i_drv,
        'o_drv': o_drv,
        'i_cmp': i_cmp,
        'o_cmp': o_cmp,
        'i_drv_opts': i_drv_opts,
        'i_cmp_opts': i_cmp_opts,
        'o_drv_opts': o_drv_opts,
        'o_cmp_opts': o_cmp_opts,
        'verbosity': verbosity
    }

    # Subcommands can do `gpsdio.open(infile, **ctx.obj['r_opts'])` instead of picking
    # individual
    r_opts = {
        'driver': ctx.obj['i_drv'],
        'compression': ctx.obj['i_cmp'],
        'do': ctx.obj['i_drv_opts'],
        'co': ctx.obj['i_cmp_opts']
    }
    w_opts = {
        'driver': ctx.obj['o_drv'],
        'compression': ctx.obj['o_cmp'],
        'do': ctx.obj['o_drv_opts'],
        'co': ctx.obj['o_cmp_opts']
    }
    ctx.obj.update(
        r_opts=r_opts,
        w_opts=w_opts
    )
