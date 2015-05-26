"""
Tools for validating GPSD messages
"""


import os
import sys
import re

import six

import gpsdio.schema


def merge_info(info_a, info_b):

    """
    Joins two info dicts from info() below
    """

    def merge_hist(a, b):
        res = dict(a)
        for key, value in six.iteritems(b):
            if key in res:
                res[key] += value
            else:
                res[key] = value
        return res

    def andnone(a, b):
        if a is None:
            return b
        if b is None:
            return a
        return a and b

    def maxnone(a, b):
        if a is None:
            return b
        if b is None:
            return a
        return max(a, b)

    def minnone(a, b):
        if a is None:
            return b
        if b is None:
            return a
        return min(a, b)

    if not info_a:
        return info_b

    is_sorted = info_a['is_sorted'] and info_b['is_sorted']
    is_sorted_files = info_a['is_sorted_files'] and info_b['is_sorted_files'] and info_a['max_timestamp'] <= info_b['min_timestamp']

    return {
        'num_rows': info_a['num_rows'] + info_b['num_rows'],
        'num_incomplete_rows': info_a['num_incomplete_rows'] + info_b['num_incomplete_rows'],
        'num_invalid_rows': info_a['num_invalid_rows'] + info_b['num_invalid_rows'],
        'lat_min': minnone(info_a['lat_min'], info_b['lat_min']),
        'lat_max': maxnone(info_a['lat_max'], info_b['lat_max']),
        'lon_min': minnone(info_a['lon_min'], info_b['lon_min']),
        'lon_max': maxnone(info_a['lon_max'], info_b['lon_max']),
        'min_timestamp': minnone(info_a['min_timestamp'], info_b['min_timestamp']),
        'max_timestamp': maxnone(info_a['max_timestamp'], info_b['max_timestamp']),
        'is_sorted': is_sorted,
        'is_sorted_files': is_sorted_files,
        'mmsi_declaration': andnone(info_a['mmsi_declaration'], info_b['mmsi_declaration']),
        'mmsi_hist': merge_hist(info_a['mmsi_hist'], info_b['mmsi_hist']),
        'msg_type_hist': merge_hist(info_a['msg_type_hist'], info_b['msg_type_hist'])
        }


def collect_info(input, error_cb=None):

    """
    Get a report about a chunk of AIS data.  Report is a dictionary with the
    following keys:

        lon_min (float) -> Minimum 'lon' value
        lon_max (float) -> Maximum 'lon' value
        lat_min (float) -> Maximum 'lat' value
        lat_max (float) -> Minimum 'lat' value
        num_rows (int)   -> Total number of rows in input file
        num_invalid_rows -> Number of malformed rows
        mmsi_hist (dict) -> {mmsi: number of rows with that MMSI}
        is_sorted (bool) -> Specifies whether the entire file is sorted by timestamp
        msg_type_hist (dict) -> {message_type: number of rows with that type}
        min_timestamp (datetime) -> Earliest timestamp
        max_timestamp (datetime) -> Latest timestamp
        mmsi_declaration (bool) -> Whether an MMSI specified in the filename
            with mmsi=NUMBER is the only mmsi inside the file.

    Example output:

        {
            'num_rows': 999,
            'num_invalid_rows': 18,
            'lat_min': -52.502449999999996,
            'lat_max': 70.80154666666668,
            'lon_min': -165.8861,
            'lon_max': 153.36407833333334,
            'min_timestamp': datetime.datetime(2014, 11, 1, 7, 59, 23),
            'max_timestamp': datetime.datetime(2014, 11, 1, 7, 59, 31),
            'is_sorted': True,
            'is_sorted_files': True,
            'mmsi_declaration': None,
            'mmsi_hist': {
                '371067000': 1,
                '203999339': 1,
                '224142870': 5,
                '413505670': 2,
                '316001649': 1,
                ...
            },
            'msg_type_hist': {
                1: 416,
                2: 3,
                3: 155,
                5: 425
            }
        }

    Parameters
    ----------
    input : iterable
        An open GPSDReader or other iterable over messages
    error_cb : function(type : str, msg : dict, exc=None : exception, trace=None : str)
        Optional callback to be called for each incomplete or invalid row if given.

    Returns
    -------
    dict
    """

    stats = {
        'lon_min': None,
        'lon_max': None,
        'lat_min': None,
        'lat_max': None,
        'num_rows': 0,
        'mmsi_hist': {},
        'msg_type_hist': {},
        'num_incomplete_rows': 0,
        'num_invalid_rows': 0,
        'is_sorted': True,
        'min_timestamp': None,
        'max_timestamp': None,
        'mmsi_declaration': None
    }

    mmsi_declaration = None
    if input.name is not None and 'mmsi=' in input.name:
        mmsi_declaration = re.findall(r"mmsi=([^,.]*)[.,]", input.name)[0]
        stats['mmsi_declaration'] = True

    # Note that this is the last row that did not throw an exception on decode and is
    # not necessarily the previous row in the input
    previous_timestamp = None
    for row in input:

        # num_rows
        stats['num_rows'] += 1

        try:
            # lon_min
            if 'lon' in row and (stats['lon_min'] is None or row['lon'] < stats['lon_min']):
                stats['lon_min'] = row['lon']

            # lon_max
            if 'lon' in row and (stats['lon_max'] is None or row['lon'] > stats['lon_max']):
                stats['lon_max'] = row['lon']

            # lat_min
            if 'lat' in row and (stats['lat_min'] is None or row['lat'] < stats['lat_min']):
                stats['lat_min'] = row['lat']

            # lat_max
            if 'lat' in row and (stats['lat_max'] is None or row['lat'] > stats['lat_max']):
                stats['lat_max'] = row['lat']

            # mmsi_hist
            if 'mmsi' in row:
                if row['mmsi'] in stats['mmsi_hist']:
                    stats['mmsi_hist'][row['mmsi']] += 1
                else:
                    stats['mmsi_hist'][row['mmsi']] = 1

                if mmsi_declaration is not None:
                    if str(row['mmsi']) != mmsi_declaration:
                        stats['mmsi_declaration'] = False

            # msg_type_hist
            if 'type' in row:
                if row['type'] in stats['msg_type_hist']:
                    stats['msg_type_hist'][row['type']] += 1
                else:
                    stats['msg_type_hist'][row['type']] = 1

            # min_timestamp
            if row.get('timestamp', None) and (stats['min_timestamp'] is None or row['timestamp'] < stats['min_timestamp']):
                stats['min_timestamp'] = row['timestamp']

            # max_timestamp
            if row.get('timestamp', None) and (stats['max_timestamp'] is None or row['timestamp'] > stats['max_timestamp']):
                stats['max_timestamp'] = row['timestamp']

            # is_sorted
            # This only executes if stats['is_sorted'] = True in order to gain
            # a little optimization.  No need to test if we already know its not sorted.
            if previous_timestamp is not None and stats['is_sorted'] and row.get('timestamp', None):
                if not row['timestamp'] >= previous_timestamp:
                    stats['is_sorted'] = False

            # num_invalid_rows
            gpsdio.schema.validate_msg(row, ignore_missing=True, skip_failures=True)
            if '__invalid__' in row:
                stats['num_invalid_rows'] += 1
                if error_cb:
                    error_cb("invalid", row)
            elif not gpsdio.schema.validate_msg(row, skip_failures=True):
                stats['num_incomplete_rows'] += 1
                if error_cb:
                    error_cb("incomplete", row)

            if row.get('timestamp', None):
                previous_timestamp = row['timestamp']

        # Encountered an error - keep track of how many
        except Exception as e:
            stats['num_invalid_rows'] += 1
            if error_cb:
                import traceback                    
                error_cb("exception", row, e, traceback.format_exc(1000))

    stats['is_sorted_files'] = True

    return stats
