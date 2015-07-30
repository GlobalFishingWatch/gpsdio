"""
gpsdio etl
"""


import logging

import click

import gpsdio
from gpsdio.cli import options


@click.command()
@click.argument('infile', required=True)
@click.argument('outfile', required=True)
@click.option(
    '-f', '--filter', 'filter_expr', metavar='EXPR', multiple=True,
    help="Apply a filtering expression to the messages."
)
@click.option(
    '--sort', 'sort_field', metavar='FIELD',
    help="Sort output messages by field.  Holds the entire file in memory and drops messages "
         "lacking the specified field."
)
@options.input_driver
@options.input_driver_opts
@options.input_compression
@options.input_compression_opts
@options.output_driver
@options.output_driver_opts
@options.output_compression
@options.output_compression_opts
@click.pass_context
def etl(ctx, infile, outfile, filter_expr, sort_field,
        input_driver, input_driver_opts, input_compression, input_compression_opts,
        output_driver, output_driver_opts, output_compression, output_compression_opts):

    """
    Format conversion, filtering, and sorting.

    Data is filtered before sorting to limit the amount of data kept in memory.

    Filtering expressions take the form of Python boolean expressions and provide
    access to fields and the entire message via a custom scope.  Each field name
    can be referenced directly and the entire messages is available via a `msg`
    variable.  It is important to remember that `gpsdio` converts `timestamps` to
    `datetime.datetime()` objects internally.

    Since fields differ by message type any expression that raises a `NameError`
    when evaluated is considered a failure.

    Any Python expression that evalues as `True` or `False` can be used so so
    expressions can be combined into a single filter using `and` or split into
    multiple by using one instance of `--filter` for each side of the `and`.

    Only process messages containing a timestamp:

    \b
        $ gpsdio ${INFILE} ${OUTFILE} \\
            -f "'timestamp' in msg"

    Only process messages from May 2010 for a specific MMSI:

    \b
        $ gpsdio ${INFIE} ${OUTFILE} \\
            -f "timestamp.month == 5 and timestamp.year == 2010"" \\
            -f "mmsi == 123456789"

    Filter and sort:

    \b
        $ gpsdio ${INFILE} ${OUTFILE} \\
            -f "timestamp.year == 2010" \\
            --sort timestamp
    """

    # TODO (1.0): Delete these lines that handle fallback to old flag locations
    input_driver = ctx.obj.get('i_drv') or input_driver
    input_compression = ctx.obj.get('i_cmp') or input_compression
    input_driver_opts = ctx.obj.get('i_drv_opts') or input_driver_opts
    input_compression_opts = ctx.obj.get('i_cmp_opts') or input_compression_opts
    output_driver = ctx.obj.get('o_drv') or output_driver
    output_compression = ctx.obj.get('o_cmp',) or output_compression
    output_driver_opts = ctx.obj.get('o_drv_opts') or output_driver_opts
    output_compression_opts = ctx.obj.get('o_cmp_opts') or output_compression_opts


    logger = logging.getLogger('gpsdio-cli-etl')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting etl')

    with gpsdio.open(infile,
                     driver=input_driver,
                     compression=input_compression,
                     do=input_driver_opts,
                     co=input_compression_opts) as src:

        with gpsdio.open(outfile, 'w',
                         driver=output_driver,
                         compression=output_compression,
                         do=output_driver_opts,
                         co=output_compression_opts) as dst:

            iterator = gpsdio.filter(src, filter_expr) if filter_expr else src
            for msg in gpsdio.sort(iterator, sort_field) if sort_field else iterator:
                dst.write(msg)
