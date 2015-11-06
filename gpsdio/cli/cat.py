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
import ujson


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

        if geojson:
            outlib = nlj
            kwargs = output_driver_opts
            kwargs.update(json_lib=kwargs.get('json_lib', ujson))
        else:
            outlib = gpsdio
            kwargs = {
                'driver': 'NewlineJSON',
                'compression': False,
                'do': output_driver_opts
            }
            kwargs.update(**ctx.obj['define'])

        out = click.get_text_stream('stdout')
        with outlib.open(out, 'w', **kwargs) as dst:
            for msg in src:
                if geojson:
                    if 'lat' in msg and 'lon' in msg:
                        # Dump datetimes to string
                        msg = gpsdio.ops.msg2geojson(base_driver.dump(msg))
                    else:
                        continue
                dst.write(msg)
