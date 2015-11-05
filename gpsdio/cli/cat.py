"""
gpsdio cat
"""


import logging

import click

import gpsdio
import gpsdio.base
from gpsdio import ops
from gpsdio.cli import options
import newlinejson as nlj


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
                     co=input_compression_opts,
                     **ctx.obj['define']) as src:

        base_driver = gpsdio.base.BaseDriver(schema=src.schema)

        # Use the newlinejson library directly for geojson output because the gpsdio
        # schema can't handle it
        out = click.get_text_stream('stdout')
        with nlj.open(out, 'w', **output_driver_opts) if geojson else \
                gpsdio.open(
                    out, 'w',
                    driver='NewlineJSON',
                    compression=False,
                    do=output_driver_opts, **ctx.obj['define']) as dst:

            for msg in src:
                if geojson:
                    if 'lat' in msg and 'lon' in msg:
                        msg = gpsdio.ops.msg2geojson(base_driver.dump(msg))
                    else:
                        continue
                dst.write(msg)
