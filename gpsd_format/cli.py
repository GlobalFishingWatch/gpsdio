"""
Commandline interface for gpsd_format
"""

import datetime
import json
import os
import sys

import click
import six

import gpsd_format
import gpsd_format.schema
import gpsd_format.validate


@click.group()
@click.pass_context
def main(ctx):
    """
    A collection of tools for working with the GPSD JSON format (or the same format in a msgpack container)
    """

    pass


@main.command()
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
    Print info about a GPSD format AIS/GPS file
    """

    if os.path.isdir(infile):
        files = [os.path.join(infile, name) for name in os.listdir(infile)]
    else:
        files = [infile]

    files.sort()

    stats = {}
    for name in files:
        sys.stderr.write("Collecting stats for {infile} ...\n".format(infile=name))
        with gpsd_format.open(name, "r", skip_failures=True, force_message=False) as f:
            if verbose:
                def error_cb(type, msg, exc=None, trace=None):
                    if exc:
                        sys.stderr.write("%s: %s: %s: %s\n" % (name, type.title(), exc, msg))
                        if trace:
                            sys.stderr.write("%s\n" % (trace,))
                    else:
                        sys.stderr.write("%s: %s: %s\n" % (name, type.title(), msg))
            else:
                error_cb = None
            stats = gpsd_format.validate.merge_info(stats, gpsd_format.validate.collect_info(f, error_cb=error_cb))

    if print_json:
        for key, value in six.iteritems(stats):
            if isinstance(value, datetime.datetime):
                stats[key] = value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        stats['file'] = infile
        sys.stdout.write(json.dumps(stats) + "\n")
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
            _min_t = gpsd_format.schema.datetime2str(stats['min_timestamp'])
        else:
            _min_t = None
        if stats['max_timestamp'] is not None:
            _max_t = gpsd_format.schema.datetime2str(stats['max_timestamp'])
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

    sys.exit(0)


@main.command()
@click.argument("infile", metavar="INPUT_FILENAME")
@click.argument("outfile", metavar="OUTPUT_FILENAME")
@click.pass_context
def convert(ctx, infile, outfile):
    """
    Converts between JSON and msgpack container formats
    """

    with gpsd_format.open(infile) as reader:
        with gpsd_format.open(outfile, 'w') as writer:
            for row in reader:
                writer.write(row)
