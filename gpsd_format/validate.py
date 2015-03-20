"""
Tools for validating GPSD messages
"""


import json
import os
import sys
import re

import gpsd_format.io
import gpsd_format.schema


# TODO: Move this to the schema?
# In order to ease test maintenance as outputs and inputs change the data structure below contains a test for every
# field, a value that will pass the test, and a value that will fail the test.  All information is pulled from GPSD
# (http://catb.org/gpsd/AIVDM.html) and assumes two things:
#   1. Fieldnames are unique across all messages
#   2. Fields appearing in different message types contain the same information.  For instance, the field 'sog'
#      appears in multiple types but is always speed over ground in the same units in every message.
#
# Keys are fieldnames and values are dictionaries containing three keys:
#   1. test - a function that verifies a value is acceptable for this field
#   2. good - a value that will pass the test function
#   3. bad  - a value that will not pass the test function
#
# Some fields are flags with values 0 or 1 that may be switched to Python's bool in the future but in the meantime
# we want to be positive these values are int's.  Since bool subclasses int expressions like `0 in (1, 0)` and
# `True in (0, 1)` both evaluate as `True` which could yield unexpected results.  Any test that expects an int
# also checks to make sure that int is NOT a bool, even if the field is a range and will never be bool.  Better to be
# safe here than be forced to debug some potentially ambiguous bugs elsewhere.
MSG_VALIDATION_LOOKUP = {

    # Comments about where fields are pulled from just reference where the description was found in the GPSD
    # specification http://catb.org/gpsd/AIVDM.html
    # They're not critical but if there is a discrepancy between what is expected and how the test is written
    # it may help us figure out why.

    # Pulled from types 1, 2, and 3 GPSD spec
    'type': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(1, 28),
        'good': 5,
        'bad': -1
    },
    'repeat': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 2 ** 2,
        'good': 4,
        'bad': -1
    },
    'mmsi': {
        'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 30,
        'good': '12345678902345678',
        'bad': 1234
    },
    'status': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 16),
        'good': 2,
        'bad': -10
    },
    'turn': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(-127, 129),
        'good': 125,
        'bad': -1000
    },
    'sog': {
        'test': lambda x: isinstance(x, float) and 0 <= x <= 102.2 or x == 1022,
        'good': 1022,
        'bad': 103
    },
    'accuracy': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
        'good': 0,
        'bad': 2,
    },
    'lat': {
        'test': lambda x: isinstance(x, float) and -90 <= x <= 90 or x == 91,
        'good': 91,
        'bad': -100
    },
    'lon': {
        # TODO: Should -180 be a valid value?  Maybe `-180 < x` instead?
        'test': lambda x: isinstance(x, float) and -180 <= x <= 180 or x == 181,
        'good': 181,
        'bad': -180.1
    },
    'course': {
        # TODO: Should -90 be a valid value?  Maybe `-90 < x` instead?
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 359 or x == 3600,
        'good': 3600,
        'bad': 360
    },
    'heading': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 359 or x == 511,
        'good': 511,
        'bad': -102
    },
    'second': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 64),
        'good': 63,
        'bad': 64
    },
    'maneuver': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (1, 2),
        'good': 2,
        'bad': 3
    },
    'raim': {
        # TODO: bool is more Pythonic if the field is actually boolean and not state
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
        'good': 0,
        'bad': -2
    },
    'radio': {
        # TODO: What will this value be?
        'test': lambda x: x is None,
        'good': None,
        'bad': False
    },

    # Pulled from type 5 GPSD spec
    'ais_version': {
        # TODO: Should always be 0 right now.  The other vals are reserved.
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1, 2, 3),
        'good': 2,
        'bad': True
    },
    'imo': {
        'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 30,
        'good': 'value',
        'bad': True,
    },
    'callsign': {
        'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 42,
        'good': 'good',
        'bad': json
    },
    'shipname': {
        'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 120,
        'good': 'good value',
        'bad': False
    },
    'shiptype': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 100),
        'good': 87,
        'bad': str
    },
    'to_bow': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 2 ** 9,
        'good': 1,
        'bad': -1
    },
    'to_stern': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 2 ** 9,
        'good': 0,
        'bad': tuple
    },
    'to_port': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 2 ** 6,
        'good': 1,
        'bad': -34
    },
    'to_starboard': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 2 ** 6,
        'good': 0,
        'bad': False,
    },
    'epfd': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 9),
        'good': 8,
        'bad': 10
    },
    'month': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 13),
        'good': 12,
        'bad': 'asdf'
    },
    'day': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 32),
        'good': 1,
        'bad': ':'
    },
    'hour': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 25),
        'good': 23,
        'bad': ','
    },
    'minute': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 61),
        'good': 54,
        'bad': '*'
    },
    'draught': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 < x <= 2 ** 8,
        'good': 1,
        'bad': 2 ** 8 + 1
    },
    'destination': {
        'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 120,
        'good': 'v',
        'bad': 2 * 2
    },
    'dte': {
        # TODO: Switch to a more Pythonic bool if this is actually bolean and not a status
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
        'good': 0,
        'bad': 8
    },

    # Pulled from type 18 GPSD spec
    'reserved': {
        'test': lambda x: x is None,
        'good': None,
        'bad': 1
    },
    'regional': {
        'test': lambda x: x is None,
        'good': None,
        'bad': -1
    },
    'speed': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x <= 2 ** 10,
        'good': 0,
        'bad': str
    },
    'cs': {
        # Not bool - state
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
        'good': 0,
        'bad': 7
    },
    'display': {
        # Not bool - state
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
        'good': 1,
        'bad': 'j'
    },
    'dsc': {
        # TODO: Switch to a more Pythonic bool?
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
        'good': 1,
        'bad': -45
    },
    'band': {
        # TODO: Switch to a more Pythonic bool?
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
        'good': 0,
        'bad': 4
    },
    'msg22': {
        # TODO: Switch to a more Pythonic bool?
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
        'good': 0,
        'bad': -2
    },
    'assigned': {
        # TODO: Switch to a more Pythonic bool?
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
        'good': 1,
        'bad': -33
    },

    # All type 19 are covered between 1, 2, 3, and 18

    # Pulled from type 24 GPSD spec
    'partno': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
        'good': 0,
        'bad': -1
    },
    'vendorid': {
        'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 18,
        'good': 'this is a gooooooooood value',
        'bad': int
    },
    'model': {
        'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 4,
        'good': 'something',
        'bad': 333
    },
    'serial': {
        'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 20,
        'good': 'pawoeiras',
        'bad': -1
    },
    'mothership_mmsi': {
        'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 30,
        'good': 'done ... finally ...',
        'bad': -200
    },

    # Pulled from type 27 GPSD spec
    'gnss': {
        'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),  # Not bool - state
        'good': 0,
        'bad': 3
    }
}


# Keys are message types and values are lists of fields that type expects
MSG_TYPE_FIELDS = {
    1: [
        'type', 'repeat', 'mmsi', 'status', 'turn', 'sog', 'accuracy', 'lat', 'lon', 'course', 'heading', 'second',
        'maneuver', 'raim', 'radio'
    ],
    2: [
        'type', 'repeat', 'mmsi', 'status', 'turn', 'sog', 'accuracy', 'lat', 'lon', 'course', 'heading', 'second',
        'maneuver', 'raim', 'radio'
    ],
    3: [
        'type', 'repeat', 'mmsi', 'status', 'turn', 'sog', 'accuracy', 'lat', 'lon', 'course', 'heading', 'second',
        'maneuver', 'raim', 'radio'
    ],
    5: [
        'type', 'repeat', 'mmsi', 'ais_version', 'imo', 'callsign', 'shipname', 'shiptype', 'to_bow', 'to_stern',
        'to_port', 'to_starboard', 'epfd', 'month', 'day', 'hour', 'minute', 'draught', 'destination', 'dte'
    ],
    18: [
        'type', 'repeat', 'mmsi', 'reserved', 'speed', 'accuracy', 'lon', 'lat', 'course', 'heading', 'second',
        'regional', 'cs', 'display', 'dsc', 'band', 'msg22', 'assigned', 'raim', 'radio', 'dte', 'assigned'
    ],
    19: [
        'type', 'repeat', 'mmsi', 'reserved', 'speed', 'accuracy', 'lon', 'lat', 'course', 'heading', 'second',
        'regional', 'shipname', 'shiptype', 'to_bow', 'to_stern', 'to_port', 'to_starboard', 'epfd', 'raim', 'dte',
        'assigned'
    ],
    24: [
        'type', 'repeat', 'mmsi', 'partno', 'shipname', 'shiptype', 'vendorid', 'model', 'serial', 'callsign',
        'to_bow', 'to_stern', 'to_port', 'to_starboard', 'mothership_mmsi'
    ],
    27: [
        'type', 'repeat', 'mmsi', 'accuracy', 'raim', 'status', 'lon', 'lat', 'speed', 'course', 'gnss'
    ]
}


def merge_info(info_a, info_b):
    """Joins two info dicts from info() below"""

    def merge_hist(a, b):
        res = dict(a)
        for key, value in b.iteritems():
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
        'is_sorted': info_a['is_sorted'] and info_b['is_sorted'],
        'mmsi_declaration': andnone(info_a['mmsi_declaration'], info_b['mmsi_declaration']),
        'mmsi_hist': merge_hist(info_a['mmsi_hist'], info_b['mmsi_hist']),
        'msg_type_hist': merge_hist(info_a['msg_type_hist'], info_b['msg_type_hist'])
        }


def collect_info(infile, verbose=False, err=sys.stderr):

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
    infile : file or iterable
        An open file-like object containing data that should be in the standard
        schema or an iterable that returns transformed messages, meaning that
        every key has already been cast to its Python type.
    verbose : bool, optional
        When an invalid row is encountered, print an error to `err`
    err : file, optional
        Stream where errors are written if `verbose=True`

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
    if hasattr(infile, 'name') and 'mmsi=' in infile.name:
        mmsi_declaration = re.findall(r"mmsi=([^,.]*)[.,]", infile.name)[0]
        stats['mmsi_declaration'] = True

    # Note that this is the last row that did not throw an exception on decode and is
    # not necessarily the previous row in the input
    previous_row = None
    for row in gpsd_format.io.GPSDReader(infile, throw_exceptions=False, force_message=False):

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
            if 'timestamp' in row and (stats['min_timestamp'] is None or row['timestamp'] < stats['min_timestamp']):
                stats['min_timestamp'] = row['timestamp']

            # max_timestamp
            if 'timestamp' in row and (stats['max_timestamp'] is None or row['timestamp'] > stats['max_timestamp']):
                stats['max_timestamp'] = row['timestamp']

            # is_sorted
            # This only executes if stats['is_sorted'] = True in order to gain
            # a little optimization.  No need to test if we already know its not sorted.
            if previous_row is not None and stats['is_sorted'] and 'timestamp' in row:
                if not row['timestamp'] >= previous_row['timestamp']:
                    stats['is_sorted'] = False

            # num_invalid_rows
            gpsd_format.schema.validate_message(row, ignore_missing=True, modify=True)
            if '__invalid__' in row:
                stats['num_invalid_rows'] += 1
                if verbose:
                    err.write("ERROR: Invalid row: {row}".format(row=row) + os.linesep)
            elif not gpsd_format.schema.validate_message(row):
                stats['num_incomplete_rows'] += 1
                if verbose:
                    err.write("WARNING: Incomplete row: {row}".format(row=row) + os.linesep)

            previous_row = row

        # Encountered an error - keep track of how many
        except Exception as e:
            stats['num_invalid_rows'] += 1
            if verbose:
                err.write("Exception: `{msg}' - row: `{row}'".format(msg=e.message, row=row) + os.linesep)

    return stats


def validate_messages(messages, err=None):

    """
    Determine whether or not an input message conforms to the Benthos spec.

    Example:

        >>> import json
        >>> with open('Messages.json') as infile:
        ...     with open('Logfile') as logfile:
        ...         print(validate_messages(
        ...             (json.loads(msg) for msg in infile), err=logfile))

    Parameters
    ----------
    msg : iter
        An iterable producing one AIS message as a dictionary every iteration.
    err : file, optional
        File-like object where errors are logged and failed messages are written.
        A message with multiple invalid fields will have multiple errors in this
        file.

    Returns
    -------
    bool
        True if every message passes
    """

    return_val = True

    for msg in messages:

        # Make sure the message specifies its type and that the type is one we can validate
        if 'type' not in msg or msg['type'] not in MSG_TYPE_FIELDS:
            if err is not None:
                err.write("No 'type' key in msg or type is invalid or not testable: %s" % msg)
            return_val = False

        # Normal field validation
        else:
            msg_type = msg['type']
            for field in MSG_TYPE_FIELDS[msg_type]:
                if not MSG_VALIDATION_LOOKUP[field]['test'](msg[field]):
                    if err is not None:
                        sys.stdout.write("Field `%s' failed: %s" % (field, json.dumps(msg) + os.linesep))
                    return_val = False

    return return_val
