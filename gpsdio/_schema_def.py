"""
The schema definitions are very long and make reading `gpsdio/schema.py` difficult
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

    if datetime_obj is None:
        return "0000-00-00T24:60:60Z"

    return datetime_obj.strftime(DATETIME_FORMAT)


def str2datetime(string):
    """
    Convert a normalized Benthos timestamp to a datetime object

    Parameters
    ----------
    string : str
        String to convert
    """

    if string == "0000-00-00T24:60:60Z":
        return None

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


# Fields required by each message type, by message type ID
fields_by_msg_type = {
    1: [
        'slot_timeout', 'sync_state', 'repeat', 'lat', 'turn', 'mmsi', 'lon', 'raim', 'heading', 'scaled', 'course',
        'second', 'status', 'type', 'device', 'spare', 'maneuver', 'class', 'speed', 'accuracy'
    ],
    2: [
        'slot_timeout', 'sync_state', 'repeat', 'lat', 'turn', 'mmsi', 'lon', 'raim', 'heading', 'scaled', 'course',
        'second', 'status', 'type', 'device', 'spare', 'maneuver', 'class', 'speed', 'accuracy'
    ],
    3: [
        'slot_timeout', 'sync_state', 'repeat', 'lat', 'turn', 'mmsi', 'lon', 'raim', 'heading', 'scaled', 'course',
        'second', 'status', 'type', 'device', 'spare', 'maneuver', 'class', 'speed', 'accuracy'],
    4: [
        'slot_timeout', 'sync_state', 'repeat', 'mmsi', 'device', 'lon', 'raim', 'scaled', 'epfd', 'transmission_ctl',
        'eta', 'spare', 'slot_number', 'lat', 'type', 'class', 'accuracy'
    ],
    5: [
        'scaled', 'to_starboard', 'repeat', 'shipname', 'ais_version', 'draught', 'mmsi', 'destination', 'to_bow',
        'dte', 'to_stern', 'to_port', 'eta', 'callsign', 'imo', 'shiptype', 'device', 'spare', 'epfd', 'type', 'class'
    ],
    6: [
        'repeat', 'retransmit', 'spare2', 'dest_mmsi', 'seqno', 'mmsi', 'dac', 'ack_required', 'scaled', 'msg_seq',
        'spare', 'fid', 'device', 'type', 'class'],
    7: [
        'repeat', 'mmsi', 'scaled', 'acks', 'device', 'type', 'class'
    ],
    8: [
        'notice_type_str', 'repeat', 'dac', 'mmsi', 'link_id', 'scaled', 'duration_minutes', 'spare', 'device',
        'sub_areas', 'class', 'notice_type', 'fid', 'type'
    ],
    9: [
        'slot_timeout', 'received_stations', 'repeat', 'spare2', 'alt_sensor', 'mmsi', 'device', 'lon', 'raim', 'dte',
        'scaled', 'course', 'second', 'spare', 'lat', 'alt', 'type', 'class', 'speed', 'accuracy'
    ],
    10: [
        'scaled', 'device', 'repeat', 'spare', 'spare2', 'dest_mmsi', 'mmsi', 'type', 'class'
    ],
    11: [
        'slot_timeout', 'sync_state', 'repeat', 'mmsi', 'device', 'lon', 'raim', 'scaled', 'epfd', 'transmission_ctl',
        'eta', 'spare', 'lat', 'slot_offset', 'type', 'class', 'accuracy'
    ],
    12: [
        'repeat', 'mmsi', 'scaled', 'spare', 'device', 'class', 'retransmit', 'seqno', 'dest_mmsi', 'type'
    ],
    13: [
        'repeat', 'mmsi', 'class', 'scaled', 'device', 'mmsi4', 'mmsi3', 'mmsi2', 'mmsi1'
    ],
    14: [
        'repeat', 'text', 'mmsi', 'scaled', 'device', 'class'
    ],
    15: [
        'spare4', 'repeat', 'slot_offset_2', 'spare3', 'spare2', 'mmsi_1', 'msg_1_1', 'mmsi', 'mmsi_2', 'class',
        'scaled', 'dest_msg_1_2', 'slot_offset_1_1', 'spare', 'device', 'type', 'msg_2', 'slot_offset_1_2'
    ],
    16: [
        'repeat', 'increment1', 'increment2', 'mmsi', 'scaled', 'spare', 'device', 'dest_mmsi_b', 'dest_mmsi_a',
        'offset1', 'offset2', 'class', 'type'
    ],
    17: [
        'scaled', 'device', 'repeat', 'spare', 'spare2', 'lat', 'type', 'mmsi', 'lon', 'class'
    ],
    18: [
        'spare2', 'scaled', 'device', 'second', 'cs', 'speed', 'unit', 'lon', 'type', 'dsc', 'msg22', 'accuracy',
        'repeat', 'mmsi', 'raim', 'band', 'spare', 'lat', 'class', 'course', 'heading', 'mode', 'display'
    ],
    19: [
        'type_and_cargo', 'spare3', 'spare2', 'to_port', 'to_bow', 'scaled', 'course', 'second', 'speed',
        'to_starboard', 'lon', 'type', 'accuracy', 'repeat', 'mmsi', 'raim', 'epfd', 'spare', 'device', 'class',
        'assigned', 'to_stern', 'lat', 'shipname', 'dte', 'heading'
    ],
    20: [
        'offset4', 'offset1', 'offset2', 'offset3', 'scaled', 'increment4', 'increment3', 'increment2', 'increment1',
        'timeout3', 'timeout2', 'timeout1', 'timeout4', 'type', 'repeat', 'mmsi', 'number4', 'number2', 'number3',
        'number1', 'device', 'class', 'spare'
    ],
    21: [
        'virtual_aid', 'to_port', 'to_bow', 'scaled', 'device', 'second', 'to_starboard', 'lon', 'type', 'accuracy',
        'repeat', 'mmsi', 'raim', 'aid_type', 'spare', 'lat', 'class', 'assigned', 'to_stern', 'shipname',
        'aton_status', 'epfd', 'off_position'
    ],
    22: [
        'repeat', 'band_b', 'zonesize', 'power', 'band_a', 'mmsi', 'spare2', 'ne_lon', 'txrx', 'scaled', 'class',
        'channel_a', 'channel_b', 'device', 'spare', 'y2', 'type', 'sw_lon', 'sw_lat', 'ne_lat'
    ],
    23: [
        'repeat', 'type_and_cargo', 'spare3', 'station_type', 'interval_raw', 'mmsi', 'ne_lon', 'quiet', 'txrx',
        'scaled', 'class', 'spare', 'device', 'spare2', 'y2', 'type', 'sw_lon', 'sw_lat', 'ne_lat'
    ],
    24: [
        'scaled', 'repeat', 'shipname', 'device', 'mmsi', 'type', 'part_num', 'class'
    ],
    25: [
        'repeat', 'dest_mmsi', 'mmsi', 'structured', 'app_id', 'scaled', 'addressed', 'device', 'data', 'class'
    ],
    27: [
        'type', 'repeat', 'mmsi', 'accuracy', 'raim', 'status', 'lon', 'lat', 'speed', 'course', 'gnss'
    ]
}



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
            'import': None,
            'export': None,
            'description': 'Course over ground - degrees from north',
            # TODO: Should -90 be a valid value?  Maybe `-90 < x` instead?
            'test': lambda x: 0.0 <= x < 360.0,
            'good': [45.0],
            'bad': [360.0]
        },
        'heading': {
            'default': 0,
            'type': int,
            'units': 'degrees',
            'import': None,
            'export': None,
            'description': 'True heading - degrees from north',
            'test': lambda x: 0 <= x <= 359 or x == 511,
            'good': [511],
            'bad': [-102]
        },
        'lat': {
            'default': 0.0,
            'type': float,
            'units': 'WGS84 degrees',
            'import': None,
            'export': None,
            'description': 'North/South coordinate in WGS84 degrees',
            'test': lambda x: -90 <= x <= 90 or x == 91,
            'good': [91.0],
            'bad': [-100.0]
        },
        'lon': {
            'default': 0.0,
            'type': float,
            'units': 'WGS84 degrees',
            'import': None,
            'export': None,
            'description': 'East/West coordinate in WGS84 degrees',
            # TODO: Should -180 be a valid value?  Maybe `-180 < x` instead?
            'test': lambda x: -180 <= x <= 180 or x == 181,
            'good': [181.0],
            'bad': [-180.1]
        },
        'mmsi': {
            'default': 1234567890,
            'type': int,
            'units': 'N/A',
            'import': None,
            'export': None,
            'description': 'Mobile Marine Service Identifier',
            'test': lambda x: not isinstance(x, bool),
            'good': [123],
            'bad': [True]
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
            'default': 0.0,
            'type': float,
            'test': lambda x: 0 <= x <= 102.2 or x == 1022,
            'good': [1022],
            'bad': [103],
            'description': '',
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'speed': {
            'default': 0.0,
            'type': float,
            'units': 'kn/h',
            'import': None,
            'export': None,
            'description': 'Speed over ground in nautical miles per hour',
            'test': lambda x: 0 <= x <= 102.2 or x == 1022,
            'good': [1022.0],
            'bad': [103.0]
        },
        'status': {
            'default': 'Not defined',
            'type': str,
            'units': 'N/A',
            'import': None,
            'export': None,
            'description': 'Navigation status (e.g. at anchor, moored, aground, etc.)',
            # TODO: Should test if in list of allowed values
            'test': lambda x: x,
            'good': ['Moored'],
            'bad': ['']
        },
        'turn': {
            'default': None,
            'null': True,
            'type': int,
            'units': 'degrees/min',
            'import': None,
            'export': None,
            'description': 'Rate of turn',
            'test': lambda x: x in range(-127, 129),
            'good': [125],
            'bad': [-1000]
        },
        'type': {
            'default': 0,
            'type': int,
            'units': 'N/A',
            'import': None,
            'export': None,
            'description': 'NMEA message code',
            'test': lambda x: x in range(1, 28),
            'good': [5],
            'bad': [-1]
        },
        'shipname': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'import': None,
            'export': None,
            'description': 'Vessel name',
            'test': lambda x: len(x) <= 2 ** 120,
            'good': ['good value'],
            'bad': [False],
            'required': False
        },
        'shiptype': {
            'default': 'Unknown',
            'type': str,
            'units': 'N/A',
            'import': None,
            'export': None,
            'description': 'Vessel type',
        },
        'callsign': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'import': None,
            'export': None,
            'description': 'Vessel callsign',
            'test': lambda x: len(x) <= 2 ** 42,
            'good': ['good'],
            'bad': [123]
        },
        'destination': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'import': None,
            'export': None,
            'description': 'UN/LOCODE or ERI terminal code'
        },
        'assigned': {
            'default': 0,
            'type': int,
            'units': 'N/A',
            'import': None,
            'export': None,
            'description': 'Assigned-mode flag',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: x in (0, 1),
            'good': [1],
            'bad': [-33],
            'required': False
        },
        'to_port': {
            'default': 0,
            'type': int,
            'units': 'meters',
            'description': 'Dimension to port',
            'test': lambda x: 0 <= x <= 2 ** 6,
            'import': None,
            'export': None,
            'good': [1],
            'bad': [-34]
        },
        'accuracy': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'import': None,
            'export': None,
            'good': [True],
            'bad': [2]
        },
        'ack_required': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'import': None,
            'export': None
        },
        'acks': {
            'default': [],
            'description': '',
            'type': list,
            'units': '',
            'import': None,
            'export': None
        },
        'aid_type': {
            'default': 'Type of Aid to Navigation not specified',
            'description': '',
            'type': str,
            'units': '',
            'import': None,
            'export': None
        },
        'ais_version': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Should always be 0 right now.  The other vals are reserved.
            'test': lambda x: not isinstance(x, bool) and x in (0, 1, 2, 3),
            'good': [2],
            'bad': [True],
            'import': None,
            'export': None
        },
        'alt': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'alt_sensor': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'aton_status': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'band': {
            'default': 1,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: x in (0, 1),
            'good': [0],
            'bad': [4],
            'import': None,
            'export': None
        },
        'band_a': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'band_b': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'channel_a': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'channel_b': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'class': {
            'default': 'AIS',
            'description': '',
            'type': str,
            'units': '',
            'import': None,
            'export': None
        },
        'cs': {
            'default': 1,
            'description': '',
            'type': int,
            'units': '',
            # Not bool - state
            'test': lambda x: x in (0, 1),
            'good': [0],
            'bad': [7],
            'import': None,
            'export': None
        },
        'dac': {
            'default': 1,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'dest_mmsi': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'dest_mmsi_a': {
            'default': '',
            'description': '',
            'type': str,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'dest_mmsi_b': {
            'default': '',
            'description': '',
            'type': str,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'dest_msg_1_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'device': {
            'default': 'stdin',
            'description': '',
            'type': str,
            'units': '',
            'import': None,
            'export': None
        },
        'display': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # Not bool - state
            'test': lambda x: x in (0, 1),
            'good': [1],
            'bad': ['j'],
            'import': None,
            'export': None
        },
        'draught': {
            'default': 0,
            'description': '',
            'type': float,
            'units': '',
            'test': lambda x: 0.0 < x <= 2 ** 8,
            'good': [1.0],
            'bad': [2 ** 8 + 1],
            'import': None,
            'export': None
        },
        'dsc': {
            'default': 1,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: x in (0, 1),
            'good': [1],
            'bad': [-45],
            'import': None,
            'export': None
        },
        'dte': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Switch to a more Pythonic bool if this is actually bolean and not a status
            'test': lambda x: x in (0, 1),
            'good': [0],
            'bad': [8],
            'import': None,
            'export': None
        },
        'duration_minutes': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'epfd': {
            'default': 'Unknown',
            'description': '',
            'type': str,
            'units': '',
            'import': None,
            'export': None
        },
        'fid': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'imo': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'increment1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'increment2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'increment3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'increment4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'interval_raw': {
            'default': 11,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'link_id': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'mmsi_1': {
            'default': '',
            'description': '',
            'type': str,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'mmsi_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'mmsi1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'mmsi2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'mmsi3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'mmsi4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'mode': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'msg22': {
            'default': 1,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: x in (0, 1),
            'good': [0],
            'bad': [-2],
            'required': False,
            'import': None,
            'export': None
        },
        'msg_1_1': {
            'default': 5,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'msg_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'msg_seq': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'name': {
            'default': '',
            'description': 'Aid-to-Navigation name',
            'type': str,
            'units': '',
            'import': None,
            'export': None
        },
        'ne_lat': {
            'default': 0.0,
            'description': '',
            'type': float,
            # Stored as str in container for some reason
            'import': float,
            'export': str,
            'units': '',
            'import': None,
            'export': None
        },
        'ne_lon': {
            'default': 0.0,
            'description': '',
            'type': float,
            # Stored as str in container for some reason
            'import': float,
            'export': str,
            'units': '',
            'import': None,
            'export': None
        },
        'notice_type': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'notice_type_str': {
            'default': 'Undefined',
            'description': '',
            'type': str,
            'units': '',
            'import': None,
            'export': None
        },
        'number1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'number2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'number3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'number4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'off_position': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'import': None,
            'export': None
        },
        'offset1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'offset2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'offset3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'offset4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'part_num': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'power': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'import': None,
            'export': None
        },
        'quiet': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'raim': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'good': [False],
            'bad': [-2],
            'import': None,
            'export': None
        },
        'received_stations': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'repeat': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: 0 <= x <= 2 ** 2,
            'good': [4],
            'bad': [-1],
            'import': None,
            'export': None
        },
        'retransmit': {
            'default': True,
            'description': '',
            'type': bool,
            'units': '',
            'import': None,
            'export': None
        },
        'scaled': {
            'default': True,
            'description': '',
            'type': bool,
            'units': '',
            'import': None,
            'export': None
        },
        'second': {
            'default': 60,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None,
            'test': lambda x: x in range(0, 64),
            'good': [63],
            'bad': [64]
        },
        'seqno': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'slot_number': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'slot_offset': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'slot_offset_1_1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'slot_offset_1_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'slot_offset_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'slot_timeout': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'spare': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'spare2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None

        },
        'spare3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None

        },
        'spare4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None

        },
        'maneuver': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: x in (0, 1, 2),
            'good': [2],
            'bad': [3],
            'import': None,
            'export': None
        },
        'station_type': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'sub_areas': {
            'default': [],
            'description': '',
            'type': list,
            'units': '',
            'import': None,
            'export': None
        },
        'sw_lon': {
            'default': 0.0,
            'description': '',
            'type': float,
            # Stored as str in container for some reason
            'import': float,
            'export': str,
            'units': '',
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
            'required': False,
            'import': None,
            'export': None
        },
        'timeout1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'timeout2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'timeout3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'timeout4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'to_bow': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # TODO: FIXME: This test is incorrect. value can not be > 511 according to AIS spec; check to_stern etc too
            'test': lambda x: 0 <= x <= 2 ** 9,
            'good': [1],
            'bad': [-1],
            'import': None,
            'export': None
        },
        'to_starboard': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: 0 <= x <= 2 ** 6,
            'good': [0],
            'bad': ['BAD'],
            'import': None,
            'export': None
        },
        'to_stern': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: 0 <= x <= 2 ** 9,
            'good': [0],
            'bad': [tuple],
            'import': None,
            'export': None
        },
        'transmission_ctl': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'txrx': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'type_and_cargo': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'unit': {
            'default': True,
            'description': '',
            'type': bool,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'virtual_aid': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'import': None,
            'export': None,
            'required': False
        },
        'y2': {
            'default': 0.0,
            'description': '',
            'type': float,
            'units': '',
            'required': False,
            'import': None,
            'export': None
        },
        'zonesize': {
            'default': 3,
            'description': '',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },


        # Our own columns
        'track': {
            'default': -1,
            'description': 'Track id for despoofed tracks',
            'type': int,
            'units': '',
            'import': None,
            'export': None
        },
        'measure_new_score': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': '',
            'import': None,
            'export': None
        },
        'measure_coursestddev': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': '',
            'import': None,
            'export': None
        },
        'measure_speedstddev': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': '',
            'import': None,
            'export': None
        },
        'measure_speedavg': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': '',
            'import': None,
            'export': None
        },
        # TODO: FIXME: Provide types etc for these
        'radio': {
            # TODO: What will this value be?
            'type': int,
            'good': [1],
            'bad': [False],
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },
        'reserved': {
            'type': int,
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },
        'regional': {
            'type': int,
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },

        # Pulled from type 24 GPSD spec
        'partno': {  # TODO: FIXME: Which one of this and partnum is the correct field name?
            'type': int,
            'test': lambda x: x in (0, 1),
            'good': [0],
            'bad': [-1],
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },
        'vendorid': {
            'type': str,
            'test': lambda x: len(x) <= 2 ** 18,
            'good': ['this is a gooooooooood value'],
            'bad': [int],
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },
        'model': {
            'type': str,
            'test': lambda x: len(x) <= 2 ** 4,
            'good': ['something'],
            'bad': [333],
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },
        'serial': {
            'type': str,
            'test': lambda x: len(x) <= 2 ** 20,
            'good': ['pawoeiras'],
            'bad': [-1],
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },
        'mothership_mmsi': {
            'type': str,
            'test': lambda x: len(x) <= 2 ** 30,
            'good': ['done ... finally ...'],
            'bad': [-200],
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },
        'structured': {
            'default': False,
            'type': bool,
            'description': '',
            'import': None,
            'export': None,
            'units': '',
            'required': False
        },
        'app_id': {
            'default': 0,
            'type': int,
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },
        'addressed': {
            'default': False,
            'type': bool,
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },
        'data': {
            'default': '',
            'type': str,
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },
        'text': {
            'default': '',
            'type': str,
            'required': False,
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },

        # Pulled from type 27 GPSD spec
        'gnss': {
            'default': 0,
            'type': int,
            # Not bool - state
            'test': lambda x: x in (0, 1),
            'good': [0],
            'bad': [3],
            'description': '',
            'units': '',
            'import': None,
            'export': None
        },

        # libais extensions
        'shiptype_text': {
            'default': 'Unknown',
            'type': str,
            'units': 'N/A',
            'description': 'Vessel type',
            'import': None,
            'export': None
        },
        'tagblock_timestamp': {
            'default': str2datetime('1970-01-01T00:00:00.0Z'),
            'type': datetime.datetime,
            'import': str2datetime,
            'export': datetime2str,
            'units': 'N/A',
            'description': 'Timestamp from tagblock. Datetime format: {}'.format(DATETIME_FORMAT),
        },
        'tagblock_station': {
            'default': '',
            'description': '',
            'type': str,
            'units': '',
            'import': None,
            'export': None
        }
    }
}
