"""
Schema definitions and functions to transform rows
"""


from ._schema_def import VERSIONS
from ._schema_def import DATETIME_FORMAT
from ._schema_def import datetime2str
from ._schema_def import str2datetime


CURRENT = VERSIONS[max(VERSIONS.keys())]
default = {field: CURRENT[field]['default']
           for field in CURRENT.keys()
           if 'default' in CURRENT[field]}

schema_import_functions = {field: CURRENT[field]['import']
                           for field in CURRENT
                           if 'import' in CURRENT[field]}
schema_export_functions = {field: CURRENT[field]['export']
                           for field in CURRENT
                           if 'export' in CURRENT[field]}
schema_types = {field: CURRENT[field]['type']
                for field in CURRENT
                if 'type' in CURRENT[field]}
schema_cast_functions = schema_types.copy()
schema_cast_functions.update(schema_import_functions)

BaseString = str.__bases__[0]

def validate_message(row, ignore_missing=False, modify=False, schema=CURRENT):
    """
    Validate that a row contains all fields required by its type and that they
    are of the required types. Returns True if valid, False if fields are
    missing or of wrong type.
    """

    res = True

    def add_invalid(key, value):
        if modify:
            if '__invalid__' not in row:
                row['__invalid__'] = {}
            row['__invalid__'][key] = value

    try:
        for key, value in row.items():
            if key == '__invalid__':
                continue
            try:
                if key not in schema:
                    continue
                fieldschema = schema[key]
                if value is None:
                    if not fieldschema.get('null', False):
                        add_invalid(key, ("null", row.pop(key)))
                        res = False
                else:
                    vt = type(value)
                    t = fieldschema.get('type', str)
                    # Hack to allow both UTF-encoded str and unicode
                    # strings - this seems to be container dependent,
                    # and actually converting using import/export
                    # would be to expensive and this is generally not
                    # that usefull
                    if t is str or t is unicode: t = BaseString

                    # Hack to allow ints where floats should be used,
                    # as the container format might convert whole
                    # numbers into ints under our feet.
                    if t is float and vt is int or vt is long: vt = float

                    if not issubclass(vt, t):
                        add_invalid(key, (t.__name__, row.pop(key)))
                        res = False
                    elif 'test' in fieldschema and not fieldschema['test'](value):
                        add_invalid(key, ('test failed', row.pop(key)))
                        res = False
            except Exception, e:
                add_invalid(key, (str(e), row.pop(key)))
                res = False

        if not ignore_missing:
            default_keys = set(get_message_default(int(row['type']), schema=schema, optional=False).keys())
            row_keys = set(row.keys())
            if len(default_keys - row_keys) != 0:
                add_invalid('__missing_keys__', tuple(default_keys - row_keys))

                res = False
    except Exception, e:
        add_invalid('__exception__', str(e))
        res = False

    return res


def row2message(row, schema=CURRENT, keep_fields=False):

    """
    Convert a row to a valid message type by removing unrecognized fields and
    adding missing fields.  Input row must have a `type` field containing the
    message type.

    No row validation or type-casting is performed EXCEPT the `type`
    field is always forced to be an `int` in order to avoid unnecessarily
    raising an exception when a string value is encountered.  If the string
    cannot be cast to an `int` then an exception will be raised.

    Parameters
    ----------
    row : dict
        Input row - must contain a `type` key
    keep_fields : bool
        List of fields that should be kept regardless of their message validity
    schema : dict
        The schema definition to use

    Returns
    -------
    dict
        Input row forced to a specific message type
    """

    message = get_message_default(int(row['type']), schema=schema)

    # Filter out any fields that don't belong
    filtered_row = {}
    for field, val in row.iteritems():
        if keep_fields or field in message:
            filtered_row[field] = val

    message.update(filtered_row)

    return message


def import_row(row, throw_exceptions=True, cast_values=False):

    """
    Cast all values in a row from their import types as defined by the
    schema definition

    Parameters
    ----------
    row : dict
        Input row with normalized field names
    throw_exceptions: bool
        If true, reading a row with an attribute value that does not match
        the schema type for that attribute will cause an exception.
    cast_values: bool
        If true, an attempt will be made to cast values to the right types
        even for primitive types where the import type and the python type is the same.

    Returns
    -------
    dict
    """

    if cast_values:
        import_functions = schema_cast_functions
    else:
        import_functions = schema_import_functions

    # This function sometimes receives rows that are not exclusively AIS message types
    # The assumption is that the user wants them to be there since there are enough ways
    # to explicitly strip them off
    output = {}
    for field, val in row.iteritems():
        if field in import_functions:
            try:
                output[field] = import_functions[field](val)
            except Exception, e:
                if throw_exceptions:
                    raise Exception("%s: %s: %s" % (field, type(e), e))
                if '__invalid__' not in output:
                    output['__invalid__'] = {}
                output['__invalid__'][field] = val
        else:
            output[field] = val

    return output


def export_row(row, throw_exceptions=True):

    """
    Cast all values in a row to their export types as defined by the
    schema definition

    Parameters
    ----------
    row : dict
        Input row adhering to the GPSD schema
    throw_exceptions: bool
        If true, reading a row with an attribute value that does not match
        the schema type for that attribute will cause an exception.
    """

    # This function sometimes receives rows that are not exclusively AIS message types
    # The assumption is that the user wants them to be there since there are enough ways
    # to explicitly strip them off
    output = {}
    for field, val in row.items():
        if field in schema_export_functions:
            try:
                output[field] = schema_export_functions[field](val)
            except Exception, e:
                if throw_exceptions:
                    raise Exception("%s: %s: %s" % (field, type(e), e))
                if '__invalid__' not in output:
                    output['__invalid__'] = {}
                output['__invalid__'][field] = unicode(val)
        else:
            output[field] = val

    return output


def get_message_default(msg_type, schema=CURRENT, optional=True):

    """
    Get an AIS message containing nothing but default values

    Parameters
    ----------
    msg_type : int
        Message type ID
    schema : dict, optional
        Schema definition from which to extract default values
    """

    try:
        res = {field: schema[field]['default']
               for field in fields_by_message_type[msg_type]
               if 'default' in schema[field] and (optional or schema[field].get('required', True))}
        res['type'] = msg_type
        return res
    except Exception, e:
        raise ValueError("Invalid AIS message type: %s: %s" % (msg_type, e))


# Fields required by each message type, by message type ID
fields_by_message_type = {
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
