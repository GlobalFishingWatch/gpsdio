"""
gpsdio info
"""


from collections import OrderedDict
import logging
import json

import click

import gpsdio
from gpsdio.cli import options


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


@click.command(name='info')
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
    '--field-hist', 'meta_member', flag_value='field_histogram',
    help="Print only the field histogram."
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
    '--with-field-hist', is_flag=True,
    help="Include a histogram of field names and message counts."
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
@click.option(
    '--num-unique-field', 'meta_member', flag_value='num_unique_field',
    help="Print only the number of unique fields."
)
@click.option(
    '--with-all', is_flag=True,
    help="Print all available metrics."
)
@options.input_driver
@options.input_driver_opts
@options.input_compression
@options.input_compression_opts
@click.pass_context
def info(ctx, infile, indent, meta_member, with_mmsi_hist, with_type_hist, with_field_hist,
         with_all, input_driver, input_driver_opts, input_compression, input_compression_opts):

    """
    Print metadata about a datasource as JSON.

    Can optionally print a single item as a string.

    One caveat of this tool is that JSON does not support integer keys, which
    means that the keys of items like `type_histogram` and `mmsi_histogram`
    have been converted to a string when in reality they should be integers.
    Tools reading the JSON output will need account for this when parsing.
    """

    # TODO (1.0): Delete these lines that handle fallback to old flag locations
    input_driver = ctx.obj.get('i_drv') or input_driver
    input_compression = ctx.obj.get('i_cmp') or input_compression
    input_driver_opts = ctx.obj.get('i_drv_opts') or input_driver_opts
    input_compression_opts = ctx.obj.get('i_cmp_opts') or input_compression_opts


    logger = logging.getLogger('gpsdio-cli-info')
    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting info')

    if meta_member == 'mmsi_histogram':
        with_mmsi_hist = True
    if meta_member == 'type_histogram':
        with_type_hist = True
    if meta_member == 'field_histogram':
        with_field_hist = True

    xmin = ymin = xmax = ymax = None
    ts_min = ts_max = None
    mmsi_hist = {}
    type_hist = {}
    field_hist = {}
    is_sorted = True
    prev_ts = None

    with gpsdio.open(infile,
                     driver=input_driver,
                     compression=input_compression,
                     do=input_driver_opts,
                     co=input_compression_opts) as src:

        idx = 0  # In case file is empty
        for idx, msg in enumerate(src):

            ts = msg.get('timestamp')
            x = msg.get('lon')
            y = msg.get('lat')
            mmsi = msg.get('mmsi')
            type_ = msg.get('type')

            for key in msg.keys():
                field_hist.setdefault(key, 0)
                field_hist[key] += 1

            if ts is not None:

                # Adjust min and max timestamp
                if ts_min is None or ts < ts_min:
                    ts_min = ts
                if ts_max is None or ts > ts_max:
                    ts_max = ts

                # Figure out if the data is sorted by time
                if prev_ts is None:
                    prev_ts = ts
                elif (ts and prev_ts) and ts < prev_ts:
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
            type_hist.setdefault(type_, 0)
            type_hist[type_] += 1

            # MMSI histogram
            mmsi_hist.setdefault(mmsi, 0)
            mmsi_hist[mmsi] += 1

    stats = {
        'bounds': (xmin, ymin, xmax, ymax),
        'count': idx + 1,
        'min_timestamp': gpsdio.schema.datetime2str(ts_min),
        'max_timestamp': gpsdio.schema.datetime2str(ts_max),
        'sorted': is_sorted,
        'num_unique_mmsi': len(set(mmsi_hist.keys())),
        'num_unique_type': len(set(type_hist.keys())),
        'num_unique_field': len(set(field_hist.keys()))
    }

    if with_all or with_mmsi_hist:
        stats['mmsi_histogram'] = OrderedDict(
            ((k, mmsi_hist[k]) for k in sorted(mmsi_hist.keys())))
    if with_all or with_type_hist:
        stats['type_histogram'] = OrderedDict(
            ((k, type_hist[k]) for k in sorted(type_hist.keys())))
    if with_all or with_field_hist:
        stats['field_histogram'] = OrderedDict(
            ((k, field_hist[k]) for k in sorted(field_hist.keys())))

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
