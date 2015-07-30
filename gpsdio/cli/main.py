"""
Main click group for the gpsdio CLI.  This must be isolated from the
other commands.
"""


import itertools
import logging
from pkg_resources import iter_entry_points
import warnings
import sys

import click
from click_plugins import with_plugins
import str2type.ext

import gpsdio
import gpsdio.drivers


@with_plugins(plugins=(
    ep for ep in itertools.chain(*(iter_entry_points('gpsdio.gpsdio_commands'),
                                 iter_entry_points('gpsdio.gpsdio_plugins'),
                                   iter_entry_points('gpsdio.cli_plugins')))))
@click.group()
@click.version_option(gpsdio.__version__)
@click.option('-v', '--verbose', count=True, help="Increase verbosity.")
@click.option('-q', '--quiet', count=True, help="Decrease verbosity.")
@click.option(
    '--i-drv', metavar='NAME', default=None,
    help='DEPRECATED: Specify the input driver.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers._BaseDriver.by_name.keys()))
)
@click.option(
    '--o-drv', metavar='NAME', default=None,
    help='DEPRECATED: Specify the output driver.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers._BaseDriver.by_name.keys()))
)
@click.option(
    '--i-cmp', metavar='NAME', default=None,
    help='DEPRECATED: Input compression format.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers._BaseCompressionDriver.by_name.keys()))
)
@click.option(
    '--o-cmp', metavar='NAME', default=None,
    help='DEPRECATED: Output compression format.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers._BaseCompressionDriver.by_name.keys()))
)
@click.option(
    '--i-drv-opt', '--ido', 'i_drv_opts', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help='DEPRECATED: Input driver options.  JSON values are automatically decoded.',
)
@click.option(
    '--i-cmp-opt', '--ico', 'i_cmp_opts', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help='DEPRECATED: Input compression driver options.  JSON values are automatically decoded.',
)
@click.option(
    '--o-drv-opt', '--odo', 'o_drv_opts', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help='DEPRECATED: Output driver options.  JSON values are automatically decoded.',
)
@click.option(
    '--o-cmp-opt', '--oco', 'o_cmp_opts', metavar='NAME=VAL', multiple=True,
    callback=str2type.ext.click_cb_key_val,
    help='DEPRECATED: Output compression driver options.  JSON values are automatically decoded.',
)
@click.pass_context
def main_group(ctx, i_drv, o_drv, i_cmp, o_cmp, i_drv_opts, i_cmp_opts, o_drv_opts, o_cmp_opts,
               verbose, quiet):
    """
    gpsdio command line interface
    """

    verbosity = max(10, 30 - 10 * verbose) - quiet
    logging.basicConfig(stream=sys.stderr, level=verbosity)

    class _DepDict(dict):

        def __getitem__(self, item):
            _dep_keys = (
                'i_drv', 'o_drv', 'i_cmp', 'o_cmp', 'i_drv_opts', 'i_cmp_opts', 'o_drv_opts',
                'o_cmp_opts', 'driver', 'compression', 'do', 'co', 'driver', 'compression',
                'do', 'co', 'r_opts', 'w_opts')
            if item in _dep_keys:
                warnings.warn(
                    "Most of the keys in the gpsdio CLI's ctx.obj will be removed by 1.0 in "
                    "favor of more centralized options.  Use the decorators in "
                    "gpsdio/cli/options.py on subcommands rather than relying on ctx.obj.",
                    FutureWarning, stacklevel=2)

            return super(_DepDict, self).__getitem__(item)

    ctx.obj = {
        'verbosity': verbosity,  # DO NOT DEPRECATE THIS KEY
        'i_drv': i_drv,
        'o_drv': o_drv,
        'i_cmp': i_cmp,
        'o_cmp': o_cmp,
        'i_drv_opts': i_drv_opts,
        'i_cmp_opts': i_cmp_opts,
        'o_drv_opts': o_drv_opts,
        'o_cmp_opts': o_cmp_opts,
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

    # Inform developers when they grab a deprecated key
    ctx.obj = _DepDict(ctx.obj)

    for k, v in ctx.obj.items():
        if k not in ('verbosity', 'r_opts', 'w_opts') and v:  # r/w opts always eval as True
            warnings.warn(
                "Input/output driver/compression flags have been moved to subcommands and will be "
                "removed from the main command in gpsdio 1.0.",
                FutureWarning,
                stacklevel=2
            )
