"""
gpsdio cat
"""


import logging

import click

import gpsdio
from gpsdio import ops
from gpsdio.cli import options


logger = logging.getLogger('gpsdio')


@click.command(name='cat')
@click.argument('infile', required=True)
@click.option(
    '--geojson', is_flag=True,
    help="Experimental.  Print messages as GeoJSON.  Non-positional messages are dropped.")
@options.input_driver
@options.input_compression
@options.input_driver_opts
@options.input_compression_opts
@options.output_driver_opts
@click.pass_context
def cat(ctx, infile, input_driver, geojson,
        input_compression, input_driver_opts, input_compression_opts, output_driver_opts):

    """
    Print messages to stdout as newline JSON.
    """

    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting cat')

    with gpsdio.open(infile,
                     driver=input_driver,
                     compression=input_compression,
                     do=input_driver_opts,
                     co=input_compression_opts) as src:

        with gpsdio.open('-', 'w',
                         driver='NewlineJSON',
                         compression=False,
                         do=output_driver_opts) as dst:
            iterator = ops.geojson(src) if geojson else src
            for msg in iterator:
                dst.write(msg)
