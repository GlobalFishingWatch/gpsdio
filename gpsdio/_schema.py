"""
AIVDM schema


Field Definitions
-----------------

* validate - Callable object validating field content.
* units - Human readable units.
* description - Human readable field description.
* default - Default value.
* name - Use this name instead of the dict key.  Optional.
"""


import six
from voluptuous import All, Any, Schema, Range, In


_FIELDS = {
    'type': {
        'validate': int,
        'units': 'N/A',
        'description': "Message type - dictates the message schema.  This value is normally "
                       "1 - 27 (with 28 - 63 reserved) but gpsdio only enforces type to allow "
                       "users to define their own message types.  It is advisable to stay out "
                       "of the active and reserved ranges."
    },
    'repeat': {
        'validate': Range(0, 3),
        'units': 'N/A',
        'description': "A directive to an AIS transceiver that this message should be "
                       "rebroadcast.  Intended as a way of getting AIS messages around hills "
                       "and other obstructions in coastal waters, but is little used as base "
                       "station coverage is more effective.  It is intended that the bit be "
                       "incremented on each retransmission, to a maximum of 3 hops.  A value "
                       "of 3 indicates 'Do not repeat'.",
        'default': 0,
    },
    'mmsi': {
        'validate': int,
        'units': 'N/A',
        'description': "Mobile Marine Service Identifier.  The official AIVDM spec requires "
                       "MMSI values to be 9 digits, but gpsdio only enforces type to support "
                       "non-AIS data sources and analysis of invalid values."
    },
    'status': {
        'validate': All(int, Range(0, 15)),
        'units': 'N/A',
        'description': "Navigation status.",
        'default': 15
    },
    'turn': {  # TODO: Finish.  libais gives a float but spec says int?
        'validate': Any(int, float),
        'units': "Degrees / minute",
        'description': "TODO: Finish.",
        'default': 128,
    },
    'speed': {  # TODO: libais can give 102.30000305175781
        'validate': All(Any(float, int), Any(Range(0, 102), In([1022, 1023, 1022.0, 1023.0]))),
        'units': "knots",
        'description': "Speed over ground is in 0.1-knot resolution from 0 to 102 knots. "
                       "Value 1023 indicates speed is not available, value 1022 indicates "
                       "102.2 knots or higher.",
        'default': 1023
    },
    'accuracy': {
        'validate': All(int, In([0, 1])),
        'description': "The position accuracy flag indicates the accuracy of the fix. A "
                       "value of 1 indicates a DGPS-quality fix with an accuracy of "
                       "< 10ms. 0, the default, indicates an unaugmented GNSS fix with "
                       "accuracy > 10m.",
        'default': 0
    },
    'lon': {
        'validate': Any(int, float),
        'units': 'WGS84 degrees',
        'description': "East/West coordinate in WGS84 degrees.  Special value '181' "
                       "indicates not available.  Would normally be constrained to -180/180 "
                       "but some interesting tracks can appear out of bounds.",
        'default': 181
    },
    'lat': {
        'validate': Any(int, float),
        'units': 'WGS84 degrees',
        'description': "North/South coordinate in WGS84 degrees.  Special value '91' "
                       "indicates not available.  Would normally be constrained to -90/90 but "
                       "some interesting tracks can appear out of bounds.",
        'default': 91
    },
    'course': {
        'validate': All(
            Any(int, float), Any(Range(0, 360, max_included=False), In([3600, 3600.0]))),
        'units': 'degrees',
        'description': "Course over ground - degrees from true north to 0.1 degree precision",
        'default': 3600.0
    },
    'heading': {
        'validate': All(int, Any(Range(0, 359), In([511]))),
        'units': 'degrees',
        'description': 'True heading - degrees from north',
        'default': 511
    },
    'second': {
        'validate': All(int, Range(0, 60)),
        'units': 'N/A',
        'description': "UTC second.",
        'default': 60
    },
    'maneuver': {
        'validate': All(int, In([0, 1, 2])),
        'units': "N/A",
        'description': "Indicates whether a special maneuver is in progress.",
        'default': 0
    },
    'raim': {
        'validate': All(int, In([0, 1])),
        'units': "N/A",
        'description': "The RAIM flag indicates whether Receiver Autonomous Integrity "
                       "Monitoring is being used to check the performance of the EPFD.",
        'default': 0
    },
    'regional': {  # TODO: Not sure this is correct
        'validate': int,
        'units': 'N/A',
        'description': "Intended for use by local maritime authorities.",
        'default': 0
    },
    'radio': {  # TODO: Not sure this is correct.
        'validate': int,
        'units': 'N/A',
        'description': "Diagnostic information for the radio system.",
        'default': 0
    },
    'year': {
        'validate': All(int, Range(0, 9999)),
        'units': 'N/A',
        'description': "UTC year.",
        'default': 0
    },
    'month': {
        'validate': All(int, Range(0, 12)),
        'units': 'N/A',
        'description': "UTC month.",
        'default': 0
    },
    'day': {
        'validate': All(int, Range(0, 31)),
        'units': 'N/A',
        'description': "UTC day.",
        'default': 0
    },
    'hour': {
        'validate': All(int, Range(0, 23)),
        'units': 'N/A',
        'description': "UTC hour.",
        'default': 0
    },
    'minute': {
        'validate': All(int, Range(0, 60)),
        'units': 'N/A',
        'description': "UTC minute.",
        'default': 60
    },
    'epfd': {  # TODO: Better description
        'validate': All(int, Range(0, 15)),
        'units': 'N/A',
        'description': "Equivalent Power-Flux Density.",
        'default': 0
    },
    'ais_version': {
        'validate': All(int, In([0, 1, 2, 3])),
        'units': 'N/A',
        'description': "Version of AIS broadcast.  Currently only ITU1371.",
        'default': 0
    },
    'imo': {  # TODO: Better description and a default (?)
        'validate': int,
        'units': 'N/A',
        'description': "Ship ID number.",
    },
    'callsign': {  # TODO: Does voluptuous have a better NoneType test?
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "Vessel callsign",
        'default': None
    },
    'shiptype': {
        'validate': All(int, Range(0, 99)),
        'units': 'N/A',
        'description': "Vessel type.  Value maps to a description.",
        'default': 0
    },
    'to_bow': {
        'validate': All(int, Range(0)),
        'units': 'meters',
        'description': "Distance from the AIS transponder to the bow of the vessel in "
                       "meters.  The special value '511' indicates 511 meters or greater.  "
                       "Negative values are accepted.",
        'default': 0
    },
    'to_stern': {
        'validate': All(int, Range(0)),
        'units': 'meters',
        'description': "Distance from the AIS transponder to the stern of the vessel in "
                       "meters.  The special value '511' indicates 511 meters or greater.  "
                       "Negative values are accepted.",
        'default': 0
    },
    'to_port': {
        'validate': All(int, Range(0)),
        'units': 'meters',
        'description': "Distance from the AIS transponder to the port side of the vessel in "
                       "meters.  The special value '63' indicates 63 meters or greater.  "
                       "Negative values are accepted.",
        'default': 0
    },
    'to_starboard': {
        'validate': All(int, Range(0)),
        'units': 'meters',
        'description': "Distance from the AIS transponder to the pstarboard ort side of the "
                       "vessel in meters.  The special value '63' indicates 63 meters or "
                       "greater.",
        'default': 0
    },
    'draught': {  # TODO: The spec says `meters / 10` (decimeters), but maybe should be meters?
        'validate': All(Any(int, float), Range(0)),
        'units': 'decimeters',
        'description': "Vessel draught in meters.",
        'default': 0
    },
    'dte': {
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "",  # TODO: Need a description
        'default': 1
    },
    'seqno': {  # TODO: What are valid values?
        'validate': All(int, In([0, 1, 2, 3])),
        'units': 'N/A',
        'description': "TODO: description",
        'default': 0
    },
    'dest_mmsi': {
        'validate': int,
        'units': 'N/A',
        'description': "Message is asking for a response from this MMSI.",  # TODO: Description
        'default': 0  # TODO: Not valid MMSI, but seems like this should have a default
    },
    'retransmit': {    # TODO: Make boolean?  Check what libais does.
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "If True, the message was re-broadcast by an intermediary station.",
        'default': 0
    },
    'dac': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "Designated Area Code / jurisdiction code.",
        'default': 0  # TODO: Is this a valid default?
    },
    'fid': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "Functional ID.  Sometimes abbreviated as FI.",
        'default': 0  # TODO: Is this a valid default?
    },
    'data': {
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "Binary data.",  # TODO: Better description
        'default': None
    },
    'mmsi1': {  # TODO: Finish - see Type 7
        'validate': int,
        'units': 'N/A',
        'description': "",
        'default': 0
    },
    'mmsiseq1': {  # TODO: Finish - see Type 7
        'validate': int,
        'units': 'N/A',
        'description': "Not used.",
        'default': 0
    },
    'mmsi2': {  # TODO: Finish - see Type 7
        'validate': int,
        'units': 'N/A',
        'description': "Interrogated MMSI.",
        'default': 0
    },
    'mmsiseq2': {  # TODO: Finish - see Type 7
        'validate': int,
        'units': 'N/A',
        'description': "Not used.",
        'default': 0
    },
    'mmsi3': {  # TODO: Finish - see Type 7
        'validate': int,
        'units': 'N/A',
        'description': "Interrogated MMSI.",
        'default': 0
    },
    'mmsiseq3': {  # TODO: Finish - see Type 7
        'validate': int,
        'units': 'N/A',
        'description': "Not used.",
        'default': 0
    },
    'mmsi4': {  # TODO: Finish - see Type 7
        'validate': int,
        'units': 'N/A',
        'description': "Interrogated MMSI.",
        'default': 0
    },
    'mmsiseq4': {  # TODO: Finish - see Type 7
        'validate': int,
        'units': 'N/A',
        'description': "Not used.",
        'default': 0
    },
    'alt': {
        'validate': All(int, Range(0, 4095)),
        'units': 'meters',
        'description': "SAR vehicle altitude.  Special value '4095' indicates altitude not "
                       "available.",
        'default': 4095
    },
    'speed9': {
        'validate': All(int, Range(0, 1023)),
        'units': 'knots',
        'description': "Broadcast by search-and-rescue aircraft.  Special value 1023 "
                       "indicates speed not available.",
        'default': 1023,
        'name': 'speed',
    },
    'assigned': {
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "Assigned-mode flag.  0=autonomous and 1=assigned.",
        'default': 0
    },
    'text': {
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "Plain text info specific to broadcast message type.",
        'default': None
    },
    'type1_1': {  # TODO: Valid default?
        'validate': All(int, Range(0, 27)),
        'units': 'N/A',
        'description': "First message type.",
        'default': 0
    },
    'offset1_1': {  # TODO: Valid default?
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "First slot offset.",
        'default': 0
    },
    'offset1_2': {  # TODO: Valid default?
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "Second slot offset.",
        'default': 0
    },
    'offset2_1': {  # TODO: Valid default?
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: What is this?",
        'default': 0
    },
    'type1_2': {
        'validate': All(int, Range(0, 27)),
        'units': 'N/A',
        'description': "Second message type.",
        'default': 0
    },
    'type2_1': {
        'validate': All(int, Range(0, 27)),
        'units': 'N/A',
        'description': "TODO: What is this?",
        'default': 0
    },
    'offset1': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: What is this?  Valid default?",
        'default': 0
    },
    'offset2': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: What is this?  Valid default?",
        'default': 0
    },
    'offset3': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: What is this?  Valid default?",
        'default': 0
    },
    'offset4': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: What is this?  Valid default?",
        'default': 0
    },
    'increment1': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: What is this?  Valid default?",
        'default': 0
    },
    'increment2': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: What is this?  Valid default?",
        'default': 0
    },
    'increment3': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: What is this?  Valid default?",
        'default': 0
    },
    'increment4': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: What is this?  Valid default?",
        'default': 0
    },
    'spare': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "Spare bits.",
        'default': 0
    },
    'cs': {
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "Carrier sense unit.  TODO: Finish",
        'default': 0
    },
    'display': {  # TODO: Boolean.  Valid default?
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "0=Does not have visual display.  1=Has visual display.  TODO: Finish.",
        'default': 0
    },
    'dsc': {  # TODO: Boolean.  Valid default?
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "If 1, unit is attached to a VHF voice radio with DSC capability.",
        'default': 1
    },
    'band': {  # TODO: Boolean.  Valid default?
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "Base stations can command units to switch frequency.  If this flag "
                       "is 1, the unit can use any part of the marine channel.",
        'default': 0
    },
    'msg22': {  # TODO: Boolean.  Valid default?
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "If 1, unit can accept a channel assignment via Message Type 22.",
        'default': 0
    },
    'number1': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "Consecutive/reserved slots.  TODO: What is this exactly?",
        'default': 0
    },
    'number2': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "Consecutive/reserved slots.  TODO: What is this exactly?",
        'default': 0
    },
    'number3': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "Consecutive/reserved slots.  TODO: What is this exactly?",
        'default': 0
    },
    'number4': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "Consecutive/reserved slots.  TODO: What is this exactly?",
        'default': 0
    },
    'timeout1': {
        'validate': All(int, Range(0, 59)),
        'units': 'minutes',
        'description': "Allocation timeout in minutes.  TODO: Valid default?",
        'default': 0
    },
    'timeout2': {
        'validate': All(int, Range(0, 59)),
        'units': 'minutes',
        'description': "Allocation timeout in minutes.  TODO: Valid default?",
        'default': 0
    },
    'timeout3': {
        'validate': All(int, Range(0, 59)),
        'units': 'minutes',
        'description': "Allocation timeout in minutes.  TODO: Valid default?",
        'default': 0
    },
    'timeout4': {
        'validate': All(int, Range(0, 59)),
        'units': 'minutes',
        'description': "Allocation timeout in minutes.  TODO: Valid default?",
        'default': 0
    },
    'aid_type': {
        'validate': All(int, Range(0, 31)),
        'units': 'N/A',
        'description': "Navigation aid type.",
        'default': 0
    },
    'name_extension': {  # TODO: Valid default?
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "TODO: Finish.  Is this a good field name?",
        'default': None
    },
    'txrx': {  # TODO: Valid default?
        'validate': All(int, In([0, 1, 2, 3])),
        'units': 'N/A',
        'description': "The txrx field encodes the same information as the 2-bit field txrx "
                       "field in message type 23; only the two low bits are used.  It also "
                       "tells the affected stations which channel or channels they may "
                       "transmit on. The options refer to the same A and B VHF channels as in "
                       "Message Type 22.",
        'default': 0
    },
    'power': {  # TODO: Valid default?
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "Low=0, high=1",
        'default': 0
    },
    'ne_lon': {
        'validate': Any(float, In([0x1a838])),
        'units': 'WGS84 degress',
        'description': "TODO: Description.",
        'default': 0x1a838
    },
    'ne_lat': {
        'validate': Any(float, In([0xd548])),
        'units': 'WGS84 degress',
        'description': "TODO: Description.",
        'default': 0xd548
    },
    'sw_lon': {
        'validate': Any(float, In([0x1a838])),
        'units': 'WGS84 degress',
        'description': "TODO: Description.",
        'default': 0x1a838
    },
    'sw_lat': {
        'validate': Any(float, In([0x1a838])),
        'units': 'WGS84 degress',
        'description': "TODO: Description.",
        'default': 0x1a838
    },
    'dest1': {  # TODO: Valid default?
        'validate': int,
        'units': 'N/A',
        'description': "MMSI of destination 1.",
        'default': 0
    },
    'dest2': {
        'validate': int,
        'units': 'N/A',
        'description': "MMSI of destination 2.",
        'default': 0
    },
    'band_a': {  # TODO: Boolean?
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "Default=0, 1=12.5kHz",
        'default': 0
    },
    'band_b': {  # TODO: Boolean?
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "Default=0, 1=12.5kHz",
        'default': 0
    },
    'zonesize': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "Size of transitional zone.",
        'default': 0
    },
    'station_type': {
        'validate': All(int, Range(0, 15)),
        'units': 'N/A',
        'description': "TODO: Finish.",
        'default': 0
    },
    'ship_type': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: Finish.  Ship type list not present in AIVDM doc.",
        'default': 0
    },
    'interval': {
        'validate': All(int, Range(0, 15)),
        'units': 'N/A',
        'description': "TODO: Finish.  Valid default?",
        'default': 0
    },
    'quiet': {
        'validate': All(int, Range(0, 15)),
        'units': 'minutes',
        'description': "Quiet time in minutes.  None=0.",
        'default': 0
    },
    'partno': {  # TODO: Valid default?
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "If the Part Number field is 0, the rest of the message is interpreted "
                       "as a Part A; if it is 1, the rest of the message is interpreted as a "
                       "Part B; values 2 and 3 are not allowed.",
        'default': 0
    },
    'vendorid': {
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "Name of the AIS equipment vendor.",
        'default': None
    },
    'model': {  # TODO: Valid default?
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "AIS equipment model number.",
        'default': 0
    },
    'serial': {
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "AIS equipment serial number.",
        'default': 0
    },
    'mothership_mmsi': {  # TODO: Valid default?
        'validate': int,
        'units': 'N/A',
        'description': "If vessel is a support craft, this is the MMSI of the vessel it is "
                       "supporting.",
        'default': 0
    },
    'addressed': {  # TODO: Boolean?  Valid default?
        'validate': All(int, In([0])),
        'units': 'N/A',
        'description': "broadcast=0, addressed=1",
        'default': 0
    },
    'structured': {  # TODO: Is validation correct?  Default?
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "TODO: Finish",
        'default': None
    },
    'app_id': {  # TODO: Default?
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "TODO: Finish.",
        'default': 0
    },
    'gnss': {  # TODO: Boolean?
        'validate': All(int, In([0, 1])),
        'units': 'N/A',
        'description': "Current GNSS position=0,Not GNSS position=1",
        'default': 1
    },
    'destination': {
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "UN/LOCODE or ERI terminal code.",
        'default': None
    },
    'shipname': {
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "Vessel name.",
        'default': None
    },
    'reserved': {
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "Bits reserved for future use.",
        'default': None
    },
    'name': {
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "Name of aid to navigation for type 21.",
        'default': None
    },
    'off_position': {
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "TODO: Finish.  Valid types?",
        'default': None
    },
    'virtual_aid': {
        'validate': Any(str, In([None])),
        'units': 'N/A',
        'description': "TODO: Finish.  Valid types?",
        'default': None
    },
    'channel_a': {  # TODO: Valid default?
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "The values of the channel_a and channel_b fields are ITU frequency "
                       "designators for channelas A and B. Normally these will be 2087 and "
                       "2088, the AIS 1 and AIS 2 frequencies of 87B (161.975 MHz) and 88B "
                       "(162.025 MHz) respectively. Regional authorities may set different "
                       "frequencies.",
        'default': 2087
    },
    'channel_b': {  # TODO: Valid default?
        'validate': All(int, Range(0)),
        'units': 'N/A',
        'description': "The values of the channel_a and channel_b fields are ITU frequency "
                       "designators for channelas A and B. Normally these will be 2087 and "
                       "2088, the AIS 1 and AIS 2 frequencies of 87B (161.975 MHz) and 88B "
                       "(162.025 MHz) respectively. Regional authorities may set different "
                       "frequencies.",
        'default': 2088
    }
}


_FIELDS_BY_TYPE = {
    1: (  # DONE
        'accuracy', 'course', 'heading', 'lat', 'lon', 'maneuver', 'mmsi',
        'spare', 'radio', 'raim', 'repeat', 'second', 'speed', 'status',
        'turn', 'type'
    ),
    2: (  # DONE
        'accuracy', 'course', 'heading', 'lat', 'lon', 'maneuver', 'mmsi',
        'spare', 'radio', 'raim', 'repeat', 'second', 'speed', 'status',
        'turn', 'type'
    ),
    3: (  # DONE
        'accuracy', 'course', 'heading', 'lat', 'lon', 'maneuver', 'mmsi',
        'spare', 'radio', 'raim', 'repeat', 'second', 'speed', 'status',
        'turn', 'type'
    ),
    4: (  # DONE
        'accuracy', 'day', 'epfd', 'hour', 'lat', 'lon', 'minute', 'mmsi',
        'month', 'radio', 'raim', 'repeat', 'second', 'type', 'year', 'spare'
    ),
    5: (  # DONE
        'ais_version', 'callsign', 'day', 'destination', 'draught', 'dte',
        'epfd', 'hour', 'imo', 'minute', 'mmsi', 'month', 'repeat', 'shipname',
        'shiptype', 'to_bow', 'to_port', 'to_starboard', 'to_stern', 'type',
        'spare'
    ),
    6: (  # DONE
        'type', 'repeat', 'mmsi', 'seqno', 'dest_mmsi', 'retransmit', 'spare',
        'dac', 'fid', 'data'
    ),
    7: (  # DONE
        'day', 'destination', 'draught', 'dte', 'epfd', 'hour', 'minute',
        'mmsi', 'mmsi1', 'mmsi2', 'mmsi3', 'mmsi4', 'mmsiseq1', 'mmsiseq2',
        'mmsiseq3', 'mmsiseq4', 'month', 'repeat', 'type'
    ),
    8: (  # DONE
        'assigned', 'course', 'dac', 'data', 'destination', 'draught', 'dte',
        'fid', 'lat', 'minute', 'mmsi', 'radio', 'raim', 'regional', 'repeat',
        'second', 'type'
    ),
    9: (  # DONE
        'accuracy', 'alt', 'assigned', 'course', 'destination', 'draught',
        'dte', 'lat', 'lon', 'minute', 'mmsi', 'radio', 'raim', 'regional',
        'repeat', 'second', 'speed9', 'type'
    ),
    10: (  # DONE
        'assigned', 'course', 'dest_mmsi', 'destination', 'draught', 'dte',
        'lat', 'lon', 'minute', 'mmsi', 'radio', 'raim', 'regional', 'repeat',
        'second', 'type'
    ),
    11: (  # DONE
        'accuracy', 'day', 'epfd', 'hour', 'lat', 'lon', 'minute', 'mmsi',
        'month', 'radio', 'raim', 'repeat', 'second', 'type', 'year'
    ),
    12: (  # DONE
        'assigned', 'course', 'dest_mmsi', 'destination', 'draught', 'dte',
        'minute', 'mmsi', 'radio', 'raim', 'regional', 'repeat', 'retransmit',
        'second', 'seqno', 'text', 'type'
    ),
    13: (  # DONE
        'day', 'destination', 'draught', 'dte', 'epfd', 'hour', 'minute',
        'mmsi', 'mmsi1', 'mmsi2', 'mmsi3', 'mmsi4', 'mmsiseq1', 'mmsiseq2',
        'mmsiseq3', 'mmsiseq4', 'month', 'repeat', 'type'
    ),
    14: (  # DONE
        'assigned', 'course', 'destination', 'draught', 'dte', 'minute',
        'mmsi', 'radio', 'raim', 'regional', 'repeat', 'retransmit', 'second',
        'text', 'type'
    ),
    15: (  # DONE
        'destination', 'draught', 'dte', 'minute', 'mmsi', 'mmsi1', 'mmsi2',
        'offset1_1', 'offset1_2', 'offset2_1', 'radio', 'repeat', 'type',
        'type1_1', 'type1_2', 'type2_1'
    ),
    16: (  # DONE
        'destination', 'draught', 'dte', 'increment1', 'minute', 'mmsi',
        'mmsi1', 'mmsi2', 'offset1', 'offset2', 'offset2_1', 'radio', 'repeat',
        'type', 'type2_1'
    ),
    17: (  # DONE
        'data', 'lat', 'lon', 'mmsi', 'repeat', 'type'
    ),
    18: (  # DONE
        'accuracy', 'assigned', 'band', 'course', 'cs', 'display', 'dsc',
        'heading', 'lat', 'lon', 'mmsi', 'msg22', 'radio', 'raim', 'regional',
        'repeat', 'reserved', 'second', 'speed', 'type'
    ),
    19: (  # DONE
        'accuracy', 'assigned', 'course', 'dte', 'epfd', 'heading', 'lat',
        'lon', 'mmsi', 'raim', 'regional', 'repeat', 'reserved', 'second',
        'shipname', 'shiptype', 'speed', 'to_bow', 'to_port', 'to_starboard',
        'to_stern', 'type'
    ),
    20: (  # DONE
        'assigned', 'dte', 'increment1', 'increment2', 'increment3',
        'increment4', 'mmsi', 'number1', 'number2', 'number3', 'number4',
        'offset1', 'offset2', 'offset3', 'offset4', 'repeat', 'timeout1',
        'timeout2', 'timeout3', 'timeout4', 'type'
    ),
    21: (  # DONE
        'accuracy', 'aid_type', 'assigned', 'epfd', 'lat', 'lon', 'mmsi',
        'name', 'off_position', 'raim', 'regional', 'repeat', 'second',
        'to_bow', 'to_port', 'to_starboard', 'to_stern', 'type', 'virtual_aid'
    ),
    22: (  # DONE
        'addressed', 'assigned', 'band_a', 'band_b', 'channel_a', 'channel_b',
        'dest1', 'dest2', 'mmsi', 'ne_lat', 'ne_lon', 'power', 'repeat',
        'sw_lat', 'sw_lon', 'txrx', 'type', 'zonesize'
    ),
    23: (  # DONE
        'assigned', 'band_a', 'band_b', 'interval', 'mmsi', 'ne_lat', 'ne_lon',
        'quiet', 'repeat', 'ship_type', 'station_type', 'sw_lat', 'sw_lon',
        'txrx', 'type', 'zonesize'
    ),
    24: (  # DONE
        'assigned', 'callsign', 'mmsi', 'model', 'mothership_mmsi', 'partno',
        'repeat', 'serial', 'shipname', 'shiptype', 'to_bow', 'to_port',
        'to_starboard', 'to_stern', 'type', 'vendorid', 'zonesize'
    ),
    25: (  # DONE
        'addressed', 'app_id', 'assigned', 'callsign', 'data', 'dest_mmsi',
        'mmsi', 'model', 'mothership_mmsi', 'repeat', 'serial', 'structured',
        'to_bow', 'to_port', 'to_starboard', 'to_stern', 'type', 'zonesize'
    ),
    26: (  # DONE
        'addressed', 'app_id', 'assigned', 'callsign', 'data', 'dest_mmsi',
        'mmsi', 'mothership_mmsi', 'radio', 'repeat', 'serial', 'structured',
        'to_bow', 'to_port', 'to_starboard', 'to_stern', 'type', 'zonesize'
    ),
    27: (  # DONE
        'accuracy', 'assigned', 'course', 'gnss', 'lat', 'lon', 'mmsi',
        'mothership_mmsi', 'raim', 'repeat', 'speed', 'status', 'to_port',
        'to_starboard', 'to_stern', 'type', 'zonesize'
    )
}


_HUMAN_TYPE_DESCRIPTION = {
    1: "Position Report Class A",
    2: "Position Report Class A",
    3: "Position Report Class A",
    4: "Base Station Report",
    5: "Static and Voyage Related Data",
    6: "Binary Addressed Message",
    7: "Binary Acknowledge",
    8: "Binary Broadcast Message",
    9: "Standard SAR Aircraft Position Report",
    10: "UTC/Date Inquiry",
    11: "UTC/Date Response",
    12: "Addressed Safety-Related Message",
    13: "Safety-Related Acknowledgement",
    14: "Safety-Related Broadcast Message",
    15: "Interrogation",
    16: "Assignment Mode Command",
    17: "DGNSS Broadcast Binary Message",
    18: "Standard Class B CS Position Report",
    19: "Extended Class B CS Position Report",
    20: "Data Link Management Message",
    21: "Aid-to-Navigation Report",
    22: "Channel Management",
    23: "Group Assignment Command",
    24: "Static Data Report",
    25: "Single Slot Binary Message",
    26: "Multiple Slot Binary Message",
    27: "Long Range AIS Broadcast message"
}
