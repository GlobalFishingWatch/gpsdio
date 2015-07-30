"""
gpsdio cat
"""


import logging

import click

import gpsdio
from gpsdio.cli import options


@click.command(name='cat')
@click.argument('infile', required=True)
@options.input_driver
@options.input_compression
@options.input_driver_opts
@options.input_compression_opts
@options.output_driver_opts
@click.pass_context
def cat(ctx, infile, input_driver,
        input_compression, input_driver_opts, input_compression_opts, output_driver_opts):

    """
    Print messages to stdout as newline JSON.
    """

    # TODO (1.0): Delete these lines that handle fallback to old flag locations
    input_driver = ctx.obj.get('i_drv') or input_driver
    input_compression = ctx.obj.get('i_cmp') or input_compression
    input_driver_opts = ctx.obj.get('i_drv_opts') or input_driver_opts
    input_compression_opts = ctx.obj.get('i_cmp_opts') or input_compression_opts
    output_driver_opts = ctx.obj.get('o_drv_opts') or output_driver_opts

    logger = logging.getLogger('gpsdio-cli-cat')
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
            for msg in src:
                dst.write(msg)
