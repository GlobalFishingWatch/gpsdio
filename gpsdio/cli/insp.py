"""
gpsdio insp
"""


import code
import logging
import os
import sys

import click

import gpsdio
from gpsdio.cli import options


@click.command()
@click.argument('infile', required=True)
@click.option(
    '--ipython', 'interpreter', flag_value='ipython',
    help="Use IPython as the interpreter."
)
@options.input_driver
@options.input_compression
@options.input_driver_opts
@options.input_compression_opts
@click.pass_context
def insp(ctx, infile, interpreter,
         input_driver, input_compression, input_driver_opts, input_compression_opts):

    # A good idea borrowed from Fiona and Rasterio
    # https://github.com/Toblerity/Fiona
    # https://github.com/Mapbox/rasterio

    """
    Open a dataset in an interactive inspector.

    IPython will be used if it can be imported unless otherwise specified.

    Analogous to doing:

        \b
        >>> import gpsdio
        >>> with gpsdio.open(infile) as stream:
        ...     # Operations
    """

    # TODO (1.0): Delete these lines that handle fallback to old flag locations
    input_driver = ctx.obj.get('i_drv') or input_driver
    input_compression = ctx.obj.get('i_cmp') or input_compression
    input_driver_opts = ctx.obj.get('i_drv_opts') or input_driver_opts
    input_compression_opts = ctx.obj.get('i_cmp_opts') or input_compression_opts

    logger = logging.getLogger('gpsdio-cli-insp')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting insp')

    header = os.linesep.join((
        "gpsdio %s Interactive Inspector Session (Python %s)"
        % (gpsdio.__version__, '.'.join(map(str, sys.version_info[:3]))),
        'Try "help(src)" or "next(src)".'))

    with gpsdio.open(infile, driver=input_driver, compression=input_compression,
                     do=input_driver_opts, co=input_compression_opts) as src:

        scope = {
            'src': src,
            'gpsdio': gpsdio
        }

        if not interpreter:
            code.interact(header, local=scope)
        elif interpreter == 'ipython':
            import IPython
            IPython.InteractiveShell.banner1 = header
            IPython.start_ipython(argv=[], user_ns=scope)
        else:
            raise click.BadParameter("Unrecognized interpreter: {}".format(interpreter))
