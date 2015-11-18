"""
gpsdio load
"""


import logging

import click

import gpsdio
from gpsdio.cli import options


logger = logging.getLogger('gpsdio')


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

    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting load')

    with gpsdio.open(
            '-',
            driver='NewlineJSON',
            compression=False,
            do=input_driver_opts,
            **ctx.obj['idefine']) as src:

        with gpsdio.open(
                outfile, 'w',
                driver=output_driver,
                compression=output_compression,
                co=output_compression_opts,
                do=output_driver_opts,
                **ctx.obj['odefine']) as dst:

            for msg in src:
                dst.write(msg)
