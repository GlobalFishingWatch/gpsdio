"""
gpsdio load
"""


import logging

import click

import gpsdio
from gpsdio.cli import options


@click.command(name='load')
@click.argument('outfile', required=True)
@options.input_driver_opts
@options.output_driver
@options.output_compression
@options.output_driver_opts
@options.output_compression_opts
@click.pass_context
def load(ctx, outfile, input_driver_opts,
         output_driver, output_driver_opts, output_compression, output_compression_opts):

    """
    Load newline JSON msgs from stdin to a file.
    """

    # TODO (1.0): Delete these lines that handle fallback to old flag locations
    input_driver_opts = ctx.obj.get('i_drv_opts') or input_driver_opts
    output_driver = ctx.obj.get('o_drv') or output_driver
    output_compression = ctx.obj.get('o_cmp',) or output_compression
    output_driver_opts = ctx.obj.get('o_drv_opts') or output_driver_opts
    output_compression_opts = ctx.obj.get('o_cmp_opts') or output_compression_opts

    logger = logging.getLogger('gpsdio-cli-load')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting load')

    with gpsdio.open('-',
                     driver='NewlineJSON',
                     compression=False,
                     do=input_driver_opts) as src, \
            gpsdio.open(outfile, 'w',
                        driver=output_driver,
                        compression=output_compression,
                        co=output_compression_opts,
                        do=output_driver_opts) as dst:
        for msg in src:
            dst.write(msg)
