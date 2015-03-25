"""
The schema definitions are very long and make reading gpsd_format/schema.py difficult
"""


import datetime


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def datetime2str(datetime_obj):

    """
    Convert a datetime object to a normalized Benthos timestamp

    Parameters
    ----------
    datetime_obj : datetime.datetime
        A loaded datetime object
    """

    return datetime_obj.strftime(DATETIME_FORMAT)


def str2datetime(string):

    """
    Convert a normalized Benthos timestamp to a datetime object

    Parameters
    ----------
    string : str
        String to convert
    """

    ms = string[20:-1]
    ms += "000000"[:6 - len(ms)]
    return datetime.datetime(
        int(string[:4]),
        int(string[5:7]),
        int(string[8:10]),
        int(string[11:13]),
        int(string[14:16]),
        int(string[17:19]),
        int(ms))

def etastr2datetime(string):
    string = string[:-1]
    dt, t = string.split("T")
    dt = dt.split("-")        
    t = t.split(":")
    if '.' in t[-1]:
        t[-1], ms = t[-1].split(".")
        ms += "000000"[:6 - len(ms)]
        t.append(ms)
    dt = [int(i) for i in dt]
    t = [int(i) for i in t]
    dt = [1900, 1, 1][:-len(dt)] + dt
    t = t + [0, 0, 0, 0][len(t):]
    return datetime.datetime(*dt + t)


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

VERSIONS = {
    1.0: {
        'course': {
            'default': 0.0,
            'type': float,
            'units': 'degrees',
            'description': 'Course over ground - degrees from north',
            # TODO: Should -90 be a valid value?  Maybe `-90 < x` instead?
            'test': lambda x: 0.0 <= x < 360.0,
            'good': 45.0,
            'bad': 360.0
        },
        'heading': {
            'default': 0,
            'type': int,
            'units': 'degrees',
            'description': 'True heading - degrees from north',
            'test': lambda x: 0 <= x <= 359 or x == 511,
            'good': 511,
            'bad': -102
        },
        'lat': {
            'default': 0.0,
            'type': float,
            'units': 'WGS84 degrees',
            'description': 'North/South coordinate in WGS84 degrees',
            'test': lambda x: -90 <= x <= 90 or x == 91,
            'good': 91.0,
            'bad': -100.0
        },
        'lon': {
            'default': 0.0,
            'type': float,
            'units': 'WGS84 degrees',
            'description': 'East/West coordinate in WGS84 degrees',
             # TODO: Should -180 be a valid value?  Maybe `-180 < x` instead?
             'test': lambda x: -180 <= x <= 180 or x == 181,
             'good': 181.0,
             'bad': -180.1
        },
        'mmsi': {
            'default': 1234567890,
            'type': int,
            'units': 'N/A',
            'description': 'Mobile Marine Service Identifier',
            'test': lambda x: not isinstance(x, bool),
            'good': 123,
            'bad': True
        },
        'timestamp': {
            'default': str2datetime('1970-01-01T00:00:00.0Z'),
            'type': datetime.datetime,
            'import': str2datetime,
            'export': datetime2str,
            'units': 'N/A',
            'description': 'Datetime format: {}'.format(DATETIME_FORMAT)
        },
        'eta': {
            'default': str2datetime('1970-01-01T00:00:00.0Z'),
            'type': datetime.datetime,
            'import': etastr2datetime,
            'export': datetime2str,
            'units': 'N/A',
            'description': 'Datetime format: {}'.format(DATETIME_FORMAT),
            'required': False
        },
        # FIXME: Confusion over type 1 / type 18 sog/speed
        'sog': {
            'type': float,
            'test': lambda x: 0 <= x <= 102.2 or x == 1022,
            'good': 1022,
            'bad': 103,
            'description': '',
            'units': ''
        },
        'speed': {
            'default': 0.0,
            'type': float,
            'units': 'kn/h',
            'description': 'Speed over ground in nautical miles per hour',
            'test': lambda x: 0 <= x <= 102.2 or x == 1022,
            'good': 1022.0,
            'bad': 103.0
        },
        'status': {
            'default': 'Not defined',
            'type': str,
            'units': 'N/A',
            'description': 'Navigation status (e.g. at anchor, moored, aground, etc.)',
            'test': lambda x: x, # Should test if in list of allowed values
            'good': 'Moored',
            'bad': ''
        },
        'turn': {
            'default': None,
            'null': True,
            'type': int,
            'units': 'degrees/min',
            'description': 'Rate of turn',
            'test': lambda x: x in range(-127, 129),
            'good': 125,
            'bad': -1000
        },
        'type': {
            'default': 0,
            'type': int,
            'units': 'N/A',
            'description': 'NMEA message code',
            'test': lambda x: x in range(1, 28),
            'good': 5,
            'bad': -1            
        },
        'shipname': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'Vessel name',
            'test': lambda x: len(x) <= 2 ** 120,
            'good': 'good value',
            'bad': False,
            'required': False
        },
        'shiptype': {
            'default': 'Unknown',
            'type': str,
            'units': 'N/A',
            'description': 'Vessel type'
        },
        'shiptype_text': {
            'default': 'Unknown',
            'type': str,
            'units': 'N/A',
            'description': 'Vessel type'
        },
        'callsign': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'Vessel callsign',
            'test': lambda x: len(x) <= 2 ** 42,
            'good': 'good',
            'bad': 123
        },
        'destination': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'UN/LOCODE or ERI terminal code'
        },
        'assigned': {
            'default': 0,
            'type': int,
            'units': 'N/A',
            'description': 'Assigned-mode flag',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: x in (0, 1),
            'good': 1,
            'bad': -33,
            'required': False
        },
        'to_port': {
            'default': 0,
            'type': int,
            'units': 'meters',
            'description': 'Dimension to port',
            'test': lambda x: 0 <= x <= 2 ** 6,
            'good': 1,
            'bad': -34
        },
        'accuracy': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'good': True,
            'bad': 2
        },
        'ack_required': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'acks': {
            'default': [],
            'description': '',
            'type': list,
            'units': ''
        },
        'aid_type': {
            'default': 'Type of Aid to Navigation not specified',
            'description': '',
            'type': str,
            'units': ''
        },
        'ais_version': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Should always be 0 right now.  The other vals are reserved.
            'test': lambda x: not isinstance(x, bool) and x in (0, 1, 2, 3),
            'good': 2,
            'bad': True
        },
        'alt': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'alt_sensor': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'aton_status': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'band': {
            'default': 1,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: x in (0, 1),
            'good': 0,
            'bad': 4
        },
        'band_a': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'band_b': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'channel_a': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'channel_b': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'class': {
            'default': 'AIS',
            'description': '',
            'type': str,
            'units': ''
        },
        'cs': {
            'default': 1,
            'description': '',
            'type': int,
            'units': '',
            # Not bool - state
            'test': lambda x: x in (0, 1),
            'good': 0,
            'bad': 7
        },
        'dac': {
            'default': 1,
            'description': '',
            'type': int,
            'units': ''
        },
        'dest_mmsi': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'dest_mmsi_a': {
            'default': '',
            'description': '',
            'type': str,
            'units': '',
            'required': False
        },
        'dest_mmsi_b': {
            'default': '',
            'description': '',
            'type': str,
            'units': '',
            'required': False
        },
        'dest_msg_1_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'device': {
            'default': 'stdin',
            'description': '',
            'type': str,
            'units': ''
        },
        'display': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # Not bool - state
            'test': lambda x: x in (0, 1),
            'good': 1,
            'bad': 'j'
        },
        'draught': {
            'default': 0,
            'description': '',
            'type': float,
            'units': '',
            'test': lambda x: 0.0 < x <= 2 ** 8,
            'good': 1.0,
            'bad': 2 ** 8 + 1
        },
        'dsc': {
            'default': 1,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: x in (0, 1),
            'good': 1,
            'bad': -45
        },
        'dte': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Switch to a more Pythonic bool if this is actually bolean and not a status
            'test': lambda x: x in (0, 1),
            'good': 0,
            'bad': 8
        },
        'duration_minutes': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'epfd': {
            'default': 'Unknown',
            'description': '',
            'type': str,
            'units': '',
        },
        'fid': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'imo': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'increment1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'increment2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'increment3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'increment4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'interval_raw': {
            'default': 11,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'link_id': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'mmsi_1': {
            'default': '',
            'description': '',
            'type': str,
            'units': '',
            'required': False
        },
        'mmsi_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'mmsi1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'mmsi2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'mmsi3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'mmsi4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'mode': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'required': False
        },
        'msg22': {
            'default': 1,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: x in (0, 1),
            'good': 0,
            'bad': -2,
            'required': False
        },
        'msg_1_1': {
            'default': 5,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'msg_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'msg_seq': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'name': {
            'default': '',
            'description': 'Aid-to-Navigation name',
            'type': str,
            'units': ''
        },
        'ne_lat': {
            'default': 0.0,
            'description': '',
            'type': float,
            # Stored as str in container for some reason
            'import': float,
            'export': str,
            'units': ''
        },
        'ne_lon': {
            'default': 0.0,
            'description': '',
            'type': float,
            # Stored as str in container for some reason
            'import': float,
            'export': str,
            'units': ''
        },
        'notice_type': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'notice_type_str': {
            'default': 'Undefined',
            'description': '',
            'type': str,
            'units': ''
        },
        'number1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'number2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'number3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'number4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'off_position': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'offset1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'offset2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'offset3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'offset4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'part_num': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'power': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'quiet': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'raim': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'good': False,
            'bad': -2
        },
        'received_stations': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'repeat': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: 0 <= x <= 2 ** 2,
            'good': 4,
            'bad': -1
        },
        'retransmit': {
            'default': True,
            'description': '',
            'type': bool,
            'units': ''
        },
        'scaled': {
            'default': True,
            'description': '',
            'type': bool,
            'units': ''
        },
        'second': {
            'default': 60,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: x in range(0, 64),
            'good': 63,
            'bad': 64
        },
        'seqno': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_number': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'slot_offset': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'slot_offset_1_1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'slot_offset_1_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'slot_offset_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'slot_timeout': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'spare': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'spare2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False

        },
        'spare3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False

        },
        'spare4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False

        },
        'maneuver': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: x in (0, 1, 2),
            'good': 2,
            'bad': 3
        },
        'station_type': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'sub_areas': {
            'default': [],
            'description': '',
            'type': list,
            'units': ''
        },
        'sw_lon': {
            'default': 0.0,
            'description': '',
            'type': float,
            # Stored as str in container for some reason
            'import': float,
            'export': str,
            'units': ''
        },
        'sw_lat': {
            'default': 0.0,
            'description': '',
            'type': float,
            # Stored as str in container for some reason
            'import': float,
            'export': str,
            'units': ''
        },
        'sync_state': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'timeout1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'timeout2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'timeout3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'timeout4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'to_bow': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # FIXME: This test is incorrect. value can not be > 511 according to AIS spec; check to_stern etc too
            'test': lambda x: 0 <= x <= 2 ** 9,
            'good': 1,
            'bad': -1
        },
        'to_starboard': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: 0 <= x <= 2 ** 6,
            'good': 0,
            'bad': 'BAD'
        },
        'to_stern': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: 0 <= x <= 2 ** 9,
            'good': 0,
            'bad': tuple
        },
        'transmission_ctl': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'txrx': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'type_and_cargo': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False
        },
        'unit': {
            'default': True,
            'description': '',
            'type': bool,
            'units': '',
            'required': False
        },
        'virtual_aid': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'y2': {
            'default': 0.0,
            'description': '',
            'type': float,
            'units': '',
            'required': False
        },
        'zonesize': {
            'default': 3,
            'description': '',
            'type': int,
            'units': ''
        },


        # Our own columns
        'track': {
            'default': -1,
            'description': 'Track id for despoofed tracks',
            'type': int,
            'units': ''
        },
        'measure_new_score': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': ''
        },
        'measure_coursestddev': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': ''
        },
        'measure_speedstddev': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': ''
        },
        'measure_speedavg': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': ''
        },
        # FIXME: Provide types etc for these
        'radio': {
            # TODO: What will this value be?
            'type': int,
            'good': 1,
            'bad': False,
            'description': '',
            'units': ''
        },
        'reserved': {
            'type': int,
            'description': '',
            'units': ''
        },
        'regional': {
            'type': int,
            'description': '',
            'units': ''
        },

        # Pulled from type 24 GPSD spec
        'partno': { # FIXME: WHich one of this and partnum is the correct field name?
            'type': int,
            'test': lambda x: x in (0, 1),
            'good': 0,
            'bad': -1,
            'description': '',
            'units': ''
        },
        'vendorid': {
            'type': str,
            'test': lambda x: len(x) <= 2 ** 18,
            'good': 'this is a gooooooooood value',
            'bad': int,
            'description': '',
            'units': ''
        },
        'model': {
            'type': str,
            'test': lambda x: len(x) <= 2 ** 4,
            'good': 'something',
            'bad': 333,
            'description': '',
            'units': ''
        },
        'serial': {
            'type': str,
            'test': lambda x: len(x) <= 2 ** 20,
            'good': 'pawoeiras',
            'bad': -1,
            'description': '',
            'units': ''
        },
        'mothership_mmsi': {
            'type': str,
            'test': lambda x: len(x) <= 2 ** 30,
            'good': 'done ... finally ...',
            'bad': -200,
            'description': '',
            'units': ''
        },
        'structured': {
            'default': False,
            'type': bool,
            'description': '',
            'units': ''
        },
        'app_id': {
            'default': 0,
            'type': int,
            'description': '',
            'units': ''
        },
        'addressed': {
            'default': False,
            'type': bool,
            'description': '',
            'units': ''
        },
        'data': {
            'default': '',
            'type': str,
            'description': '',
            'units': ''
        },
        'text': {
            'default': '',
            'type': str,
            'required': False,
            'description': '',
            'units': ''
        },

        # Pulled from type 27 GPSD spec
        'gnss': {
            'default': 0,
            'type': int,
            'test': lambda x: x in (0, 1),  # Not bool - state
            'good': 0,
            'bad': 3,
            'description': '',
            'units': ''
        }
    }
}
