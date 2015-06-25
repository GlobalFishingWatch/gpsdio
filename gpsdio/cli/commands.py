"""
Commandline interface for `gpsdio`.
"""


import code
from collections import OrderedDict
import datetime
import json
import logging
import os
import sys
import warnings

import click
import six
import str2type.ext

import gpsdio
import gpsdio.drivers
import gpsdio.schema
import gpsdio.validate


def _cb_indent(ctx, param, value):

    """
    Click callback for `gpsdio info`'s `--indent` option to let `None` be a
    valid value so the user can disable indentation.
    """

    if value.lower().strip() == 'none':
        return None
    else:
        try:
            return int(value)
        except ValueError:
            raise click.BadParameter("Must be `None` or an integer.")


@click.command()
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
@click.pass_context
def validate(ctx, infile, print_json, verbose, msg_hist, mmsi_hist):

    """
    DEPRECATED: Print info about a GPSD format AIS/GPS file
    """

    deprecation_msg = "`gpsdio validate` is deprecated and will be removed before " \
                      "v1.0.  Switch to `gpsdio info`."
    warnings.warn(deprecation_msg, DeprecationWarning, stacklevel=2)

    logger = logging.getLogger('gpsdio-cli-validate')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug("Starting validate")

    if os.path.isdir(infile):
        files = [os.path.join(infile, name) for name in os.listdir(infile)]
    else:
        files = [infile]

    files.sort()

    stats = {}
    for name in files:
        logger.exception("Collecting stats for {infile} ...\n".format(infile=name))

        with gpsdio.open(
                name, "r",
                driver=ctx.obj['i_drv'],
                do=ctx.obj['i_drv_opts'],
                compression=ctx.obj['i_cmp'],
                co=ctx.obj['i_cmp_opts'],
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


@click.command()
@click.argument("infile", metavar="INPUT_FILENAME")
@click.argument("outfile", metavar="OUTPUT_FILENAME")
@click.pass_context
def convert(ctx, infile, outfile):

    """
    DEPRECATED - use etl instead: Converts between JSON and msgpack container formats.
    """

    deprecation_msg = "`gpsdio convert` is deprecated and will be removed before " \
                      "v1.0.  Switch to `gpsdio etl`."
    warnings.warn(deprecation_msg, DeprecationWarning, stacklevel=2)

    logger = logging.getLogger('gpsdio-cli-conver')
    logger.setLevel(ctx.obj['verbosity'])
    logging.debug('Starting convert')
    logging.warning(deprecation_msg)

    with gpsdio.open(infile) as reader:
        with gpsdio.open(outfile, 'w') as writer:
            for row in reader:
                writer.write(row)


@click.command()
@click.argument('infile', required=True)
@click.pass_context
def cat(ctx, infile):

    """
    Print messages to stdout as newline JSON.
    """

    logger = logging.getLogger('gpsdio-cli-cat')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting cat')

    with gpsdio.open(infile, **ctx.obj['r_opts']) as src:

        with gpsdio.open('-', 'w', driver='NewlineJSON', compression=False) as dst:
            for msg in src:
                dst.write(msg)


@click.command()
@click.argument('outfile', required=True)
@click.pass_context
def load(ctx, outfile):

    """
    Load newline JSON msgs from stdin to a file.
    """

    logger = logging.getLogger('gpsdio-cli-load')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting load')

    with gpsdio.open('-', driver='NewlineJSON', compression=False) as src, \
            gpsdio.open(outfile, 'w', **ctx.obj['w_opts']) as dst:
        for msg in src:
            dst.write(msg)


@click.command()
@click.argument('infile', required=True)
@click.option(
    '--no-ipython', 'use_ipython', is_flag=True, default=True,
    help="Don't use IPython, even if it is available."
)
@click.pass_context
def insp(ctx, infile, use_ipython):

    # A good idea borrowed from Fiona and Rasterio

    """
    Open a dataset in an interactive inspector.

    IPython will be used if it can be imported unless otherwise specified.

    Analogous to doing:

        \b
        >>> import gpsdio
        >>> with gpsdio.open(infile) as stream:
        ...     # Operations
    """

    logger = logging.getLogger('gpsdio-cli-insp')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting insp')

    header = os.linesep.join((
        "gpsdio %s Interactive Inspector Session (Python %s)"
        % (gpsdio.__version__, '.'.join(map(str, sys.version_info[:3]))),
        "Try `help(stream)` or `next(stream)`."
    ))

    with gpsdio.open(infile, **ctx.obj['r_opts']) as src:

        scope = {
            'stream': src,
            'gpsdio': gpsdio
        }

        try:
            import IPython
        except ImportError:
            IPython = None

        if use_ipython and IPython is not None:
            IPython.embed(header=header, user_ns=scope)
        else:
            code.interact(header, local=scope)


@click.command()
@click.option(
    '--drivers', 'item', flag_value='drivers',
    help="List of registered drivers and their I/O modes."
)
@click.option(
    '--compression', 'item', flag_value='compression',
    help='List of registered compression drivers and their I/O modes.'
)
@click.pass_context
def env(ctx, item):

    """
    Information about the gpsdio environment.
    """

    logger = logging.getLogger('gpsdio-cli-env')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting env')

    if item == 'drivers':
        for name, driver in gpsdio.drivers.BaseDriver.by_name.items():
            click.echo("%s - %s" % (name, driver.io_modes))
    elif item == 'compression':
        for name, driver in gpsdio.drivers.BaseCompressionDriver.by_name.items():
            click.echo("%s - %s" % (name, driver.io_modes))
    else:
        raise click.BadParameter('A flag is required.')


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
@click.pass_context
def etl(ctx, infile, outfile, filter_expr, sort_field):

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

    logger = logging.getLogger('gpsdio-cli-etl')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting etl')

    with gpsdio.open(infile, **ctx.obj['r_opts']) as src:

        with gpsdio.open(outfile, 'w', **ctx.obj['w_opts']) as dst:

            iterator = gpsdio.filter(src, filter_expr) if filter_expr else src
            for msg in gpsdio.sort(iterator, sort_field) if sort_field else iterator:
                dst.write(msg)


@click.command()
@click.argument('infile')
@click.option(
    '--bounds', 'meta_member', flag_value='bounds',
    help="Print only the boundary coordinates as xmin, ymin, xmax, ymax.")
@click.option(
    '--count', 'meta_member', flag_value='count',
    help="Print only the number of messages in the datasource."
)
@click.option(
    '--mmsi-hist', 'meta_member', flag_value='mmsi_histogram',
    help="Print only the MMSI histogram."
)
@click.option(
    '--type-hist', 'meta_member', flag_value='type_histogram',
    help="Print only the type histogram."
)
@click.option(
    '--with-mmsi-hist', is_flag=True,
    help="Include a histogram of MMSI counts."
)
@click.option(
    '--with-type-hist', is_flag=True,
    help="Include a histogram of message type counts."
)
@click.option(
    '--indent', metavar='INTEGER', default='4', callback=_cb_indent,
    help="Indent and pretty print output.  Use `None` to turn off indentation and make output "
         "serializable JSON. (default: 4)"
)
@click.option(
    '--min-timestamp', 'meta_member', flag_value='min_timestamp',
    help="Print only the minimum timestamp."
)
@click.option(
    '--max-timestamp', 'meta_member', flag_value='max_timestamp',
    help="Print only the maximum timestamp."
)
@click.option(
    '--sorted', 'meta_member', flag_value='sorted',
    help="Print only whether or not the datasource is sorted by timestamp."
)
@click.option(
    '--num-unique-mmsi', 'meta_member', flag_value='num_unique_mmsi',
    help="Print only the number of unique MMSI numbers."
)
@click.option(
    '--num-unique-type', 'meta_member', flag_value='num_unique_type',
    help="Print only the number of unique message types."
)
@click.pass_context
def info(ctx, infile, meta_member, with_mmsi_hist, with_type_hist, indent):

    """
    Print metadata about a datasource as JSON.

    Can optionally print a single item as a string.

    One caveat of this tool is that JSON does not support integer keys, which
    means that the keys of items like `type_histogram` and `mmsi_histogram`
    have been converted to a string when in reality they should be integers.
    Tools reading the JSON output will need account for this when parsing.
    """

    logger = logging.getLogger('gpsdio-cli-info')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting info')

    if meta_member == 'mmsi_histogram':
        with_mmsi_hist = True
    if meta_member == 'type_histogram':
        with_type_hist = True

    xmin = ymin = xmax = ymax = 0
    ts_min = ts_max = None
    mmsi_hist = {}
    type_hist = {}
    is_sorted = True
    prev_ts = None

    with gpsdio.open(infile, driver=ctx.obj['i_drv'], compression=ctx.obj['i_cmp']) as src:
        idx = 0  # In case file is empty
        for idx, msg in enumerate(src):
            ts = msg.get('timestamp')
            x = msg.get('lon')
            y = msg.get('lat')
            msg_type = msg.get('type')
            mmsi = msg.get('mmsi')

            if ts is not None:

                # Adjust min and max timestamp
                if ts_min is None or ts < ts_min:
                    ts_min = ts
                if ts_max is None or ts > ts_max:
                    ts_max = ts

                # Figure out if the data is sorted by time
                if prev_ts is None:
                    prev_ts = ts
                elif ts != prev_ts and ts < prev_ts:
                    is_sorted = False

            if x is not None and y is not None:

                # Adjust bounding box
                if xmin is None or x < xmin:
                    xmin = x
                if ymin is None or y < ymin:
                    ymin = y
                if xmax is None or x > xmax:
                    xmax = x
                if ymax is None or y > ymax:
                    ymax = y

            # Type histogram
            if msg_type in type_hist:
                type_hist[msg_type] += 1
            else:
                type_hist[msg_type] = 1

            # MMSI histogram
            if mmsi in mmsi_hist:
                mmsi_hist[mmsi] += 1
            else:
                mmsi_hist[mmsi] = 1

    stats = {
        'bounds': (xmin, ymin, xmax, ymax),
        'count': idx + 1,
        'min_timestamp': gpsdio.schema.datetime2str(ts_min),
        'max_timestamp': gpsdio.schema.datetime2str(ts_max),
        'sorted': is_sorted,
        'num_unique_mmsi': len(set(mmsi_hist.keys())),
        'num_unique_type': len(set(type_hist.keys()))
    }

    if with_mmsi_hist:
        stats['mmsi_histogram'] = OrderedDict(
            ((k, mmsi_hist[k]) for k in sorted(mmsi_hist.keys())))
    if with_type_hist:
        stats['type_histogram'] = OrderedDict(
            ((k, type_hist[k]) for k in sorted(type_hist.keys())))

    stats = OrderedDict((k, stats[k]) for k in sorted(stats.keys()))

    if meta_member:
        if isinstance(stats[meta_member], (tuple, list)):
            click.echo(" ".join((map(str, stats[meta_member]))))
        elif isinstance(stats[meta_member], (dict, bool)):
            click.echo(json.dumps(stats[meta_member], indent=indent))
        else:
            click.echo(stats[meta_member])
    else:
        click.echo(json.dumps(stats, indent=indent))
