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

VERSIONS = {
    1.0: {
        'course': {
            'default': 0.0,
            'type': float,
            'units': 'degrees',
            'description': 'Course over ground - degrees from north'
        },
        'heading': {
            'default': 0.0,
            'type': float,
            'units': 'degrees',
            'description': 'True heading - degrees from north'
        },
        'lat': {
            'default': 0.0,
            'type': float,
            'units': 'WGS84 degrees',
            'description': 'North/South coordinate in WGS84 degrees'
        },
        'lon': {
            'default': 0.0,
            'type': float,
            'units': 'WGS84 degrees',
            'description': 'East/West coordinate in WGS84 degrees'
        },
        'mmsi': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'Mobile Marine Service Identifier'
        },
        'timestamp': {
            'default': '1970-01-01T00:00:00.0Z',
            'type': datetime.datetime,
            'import': str2datetime,
            'export': datetime2str,
            'units': 'N/A',
            'description': 'Datetime format: {}'.format(DATETIME_FORMAT)
        },
        'eta': {
            'default': '1970-01-01T00:00:00.0Z',
            'type': datetime.datetime,
            'import': str2datetime,
            'export': datetime2str,
            'units': 'N/A',
            'description': 'Datetime format: {}'.format(DATETIME_FORMAT)
        },
        'speed': {
            'default': 0.0,
            'type': float,
            'units': 'kn/h',
            'description': 'Speed over ground in nautical miles per hour'
        },
        'status': {
            'default': 'Not defined',
            'type': str,
            'units': 'N/A',
            'description': 'Navigation status (e.g. at anchor, moored, aground, etc.)'
        },
        'turn': {
            'default': None,
            'null': True,
            'type': float,
            'units': 'degrees/min',
            'description': 'Rate of turn'
        },
        'type': {
            'default': 0,
            'type': int,
            'units': 'N/A',
            'description': 'NMEA message code'
        },
        'shipname': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'Vessel name'
        },
        'shiptype': {
            'default': 0,
            'type': int,
            'units': 'N/A',
            'description': 'Vessel type'
        },
        'callsign': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'Vessel callsign'
        },
        'destination': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'UN/LOCODE or ERI terminal code'
        },
        'assigned': {
            'default': False,
            'type': bool,
            'units': 'N/A',
            'description': 'Assigned-mode flag'
        },
        'to_port': {
            'default': 0,
            'type': int,
            'units': 'meters',
            'description': 'Dimension to port'
        },
        'accuracy': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
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
            'units': ''
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
            'units': ''
        },
        'aton_status': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'band': {
            'default': True,
            'description': '',
            'type': bool,
            'units': ''
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
            'default': True,
            'description': '',
            'type': bool,
            'units': ''
        },
        'dac': {
            'default': 1,
            'description': '',
            'type': int,
            'units': ''
        },
        'dest_mmsi': {
            'default': '',
            'description': '',
            'type': str,
            'units': ''
        },
        'dest_mmsi_a': {
            'default': '',
            'description': '',
            'type': str,
            'units': ''
        },
        'dest_mmsi_b': {
            'default': '',
            'description': '',
            'type': str,
            'units': ''
        },
        'dest_msg_1_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'device': {
            'default': 'stdin',
            'description': '',
            'type': str,
            'units': ''
        },
        'display': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'draught': {
            'default': 0.0,
            'description': '',
            'type': float,
            'units': ''
        },
        'dsc': {
            'default': True,
            'description': '',
            'type': bool,
            'units': ''
        },
        'dte': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'duration_minutes': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'epfd': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'fid': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'imo': {
            'default': '',
            'description': '',
            'type': str,
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
            'units': ''
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
            'units': ''
        },
        'mmsi_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'mode': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'msg22': {
            'default': True,
            'description': '',
            'type': bool,
            'units': ''
        },
        'msg_1_1': {
            'default': 5,
            'description': '',
            'type': int,
            'units': ''
        },
        'msg_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'msg_seq': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
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
            'units': ''
        },
        'ne_lon': {
            'default': 0.0,
            'description': '',
            'type': float,
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
            'units': ''
        },
        'received_stations': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'repeat': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
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
            'units': ''
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
            'units': ''
        },
        'slot_offset': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_offset_1_1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_offset_1_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_offset_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_timeout': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'spare': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'spare2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'spare3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'spare4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'maneuver': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'station_type': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
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
            'units': ''
        },
        'sync_state': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
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
            'units': ''
        },
        'to_starboard': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'to_stern': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'transmission_ctl': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'txrx': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'type_and_cargo': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'unit': {
            'default': True,
            'description': '',
            'type': bool,
            'units': ''
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
            'units': ''
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
        }

    }
}
