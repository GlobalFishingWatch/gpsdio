"""
Main click group for the gpsdio CLI.  This must be isolated from the
other commands.
"""


import logging
from pkg_resources import iter_entry_points
import sys

import click
from click_plugins import with_plugins

import gpsdio
import gpsdio.drivers


entry_points = list(iter_entry_points('gpsdio.gpsdio_commands')) \
    + list(iter_entry_points('gpsdio.gpsdio_plugins')) \
    + list(iter_entry_points('gpsdio.cli_plugins'))


@with_plugins(plugins=entry_points)
@click.group()
@click.version_option(gpsdio.__version__)
@click.option('-v', '--verbose', count=True, help="Increase verbosity.")
@click.option('-q', '--quiet', count=True, help="Decrease verbosity.")
@click.pass_context
def main_group(ctx, verbose, quiet):
    """
    gpsdio command line interface
    """

    verbosity = max(10, 30 - 10 * verbose) - quiet
    logging.basicConfig(stream=sys.stderr, level=verbosity)

    ctx.obj = {
        'verbosity': verbosity,
    }
