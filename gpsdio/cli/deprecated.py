"""
Deprecated gpsdio CLI commands
"""


import datetime
import json
import logging
import os
import sys
import warnings

import click
import six

import gpsdio
from gpsdio.cli import options


@click.command(name='validate')
@click.argument("infile", metavar="INPUT_FILENAME")
@click.option(
    '--print-json', is_flag=True,
    help="Print serializable JSON instead of text"
)
@click.option(
    '--msg-hist', is_flag=True, default=False,
    help="Print a type histogram"
)
@click.option(
    '--mmsi-hist', is_flag=True, default=False,
    help="Print a MMSI histogram"
)
@click.option(
    '-v', '--verbose', is_flag=True,
    help="Print details on individual messages")
@options.input_driver
@options.input_compression
@options.input_driver_opts
@options.input_compression_opts
@click.pass_context
def validate(ctx, infile, print_json, verbose, msg_hist, mmsi_hist,
             input_driver, input_compression, input_driver_opts, input_compression_opts):

    """
    DEPRECATED - Use `gpsdio info` instead.

    Print info about a GPSD format AIS/GPS file
    """

    # TODO (1.0): Delete these lines that handle fallback to old flag locations
    warnings.warn(
        "`gpsdio validate` is deprecated and will be removed before "
        "v1.0.  Switch to `gpsdio info`.", FutureWarning, stacklevel=2)
    input_driver = ctx.obj.get('i_drv') or input_driver
    input_compression = ctx.obj.get('i_cmp') or input_compression
    input_driver_opts = ctx.obj.get('i_drv_opts') or input_driver_opts
    input_compression_opts = ctx.obj.get('i_cmp_opts') or input_compression_opts


    logger = logging.getLogger('gpsdio-cli-validate')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug("Starting validate")

    if os.path.isdir(infile):
        files = sorted([os.path.join(infile, name) for name in os.listdir(infile)])
    else:
        files = sorted([infile])

    stats = {}
    for name in files:
        logger.exception("Collecting stats for {infile} ...\n".format(infile=name))

        with gpsdio.open(
                name, "r",
                driver=input_driver,
                do=input_driver_opts,
                compression=input_compression,
                co=input_compression_opts,
                skip_failures=True,
                force_message=False) as f:

            if verbose:
                def error_cb(type, msg, exc=None, trace=None):
                    if exc:
                        logger.exception("%s: %s: %s: %s\n" % (name, type.title(), exc, msg))
                        if trace:
                            logger.exception("%s\n" % (trace,))
                    else:
                        logger.exception("%s: %s: %s\n" % (name, type.title(), msg))
            else:
                error_cb = None
            stats = gpsdio.validate.merge_info(stats, gpsdio.validate.collect_info(f, error_cb=error_cb))

    if print_json:
        for key, value in six.iteritems(stats):
            if isinstance(value, datetime.datetime):
                stats[key] = value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        stats['file'] = infile
        click.echo(json.dumps(stats) + "\n")
        sys.exit(0)
    else:
        click.echo("")
        click.echo("=== Report for %s ===" % infile)
        click.echo("  Number of rows: %s" % stats['num_rows'])
        click.echo("  Number of incomplete rows: %s" % stats['num_incomplete_rows'])
        click.echo("  Number of invalid rows: %s" % stats['num_invalid_rows'])
        click.echo("  All files are sorted: %s" % stats['is_sorted_files'])
        click.echo("  All rows are sorted: %s" % stats['is_sorted'])
        if stats['mmsi_declaration'] is not None:
            click.echo("  All rows match declared MMSI: %s" % stats['mmsi_declaration'])
        click.echo("  Number of unique MMSI's: %s" % len(stats['mmsi_hist']))
        click.echo("  Number of message types: %s" % len(stats['msg_type_hist']))
        click.echo("")
        click.echo("  X Min: %s" % stats['lon_min'])
        click.echo("  Y Min: %s" % stats['lat_min'])
        click.echo("  X Max: %s" % stats['lon_max'])
        click.echo("  Y Max: %s" % stats['lat_max'])
        click.echo("")
        if stats['min_timestamp'] is not None:
            _min_t = gpsdio.schema.datetime2str(stats['min_timestamp'])
        else:
            _min_t = None
        if stats['max_timestamp'] is not None:
            _max_t = gpsdio.schema.datetime2str(stats['max_timestamp'])
        else:
            _max_t = None
        click.echo("  Min timestamp: %s" % _min_t)
        click.echo("  Max timestamp: %s" % _max_t)
        if mmsi_hist:
            click.echo("")
            click.echo("  MMSI histogram:")
            for mmsi in sorted(stats['mmsi_hist'].keys()):
                click.echo("    %s -> %s" % (mmsi, stats['mmsi_hist'][mmsi]))
        if msg_hist:
            click.echo("")
            click.echo("  Message type histogram:")
            for msg_type in sorted(stats['msg_type_hist'].keys()):
                click.echo("    %s -> %s" % (msg_type, stats['msg_type_hist'][msg_type]))
        click.echo("")


@click.command(name='convert')
@click.argument("infile", metavar="INPUT_FILENAME")
@click.argument("outfile", metavar="OUTPUT_FILENAME")
@click.pass_context
def convert(ctx, infile, outfile):

    """
    DEPRECATED - Use `gpsdio etl` instead.

    Converts between JSON and msgpack container formats.
    """

    warnings.warn(
        "`gpsdio convert` is deprecated and will be removed before "
        "v1.0.  Switch to `gpsdio etl`.", FutureWarning, stacklevel=2)

    logger = logging.getLogger('gpsdio-cli-conver')
    logger.setLevel(ctx.obj['verbosity'])
    logging.debug('Starting convert')

    with gpsdio.open(infile) as reader:
        with gpsdio.open(outfile, 'w') as writer:
            for row in reader:
                writer.write(row)