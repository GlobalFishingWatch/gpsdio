"""
Unittests for: gpsd_format.schema
"""


import datetime
import unittest

import gpsd_format.schema


class TestCurrentSchema(unittest.TestCase):

    def test_requirements(self):

        """
        Make sure the current schema contains required fields

        Helps to make sure that when a new field definition is added it actually
        has the required elements
        """
        required = set(('default', 'type', 'units', 'description'))
        for field, definition in gpsd_format.schema.CURRENT.items():
            req = required.copy()
            if definition.get('required', True):
                req.remove('default')
            self.assertEqual(req - set(definition.keys()), set(), "Field schema %s has missing fields: %s" % (field, req - set(definition.keys())))
            self.assertIsInstance(definition['type'], type)
            self.assertIsInstance(definition['description'], str)
            self.assertIsInstance(definition['units'], str)
            if 'import' in definition:
                self.assertTrue(hasattr(definition['import'], '__call__'))
            if 'export' in definition:
                self.assertTrue(hasattr(definition['export'], '__call__'))

class TestValidateMessage(unittest.TestCase):
    def test_invalid(self):
        self.assertFalse(
            gpsd_format.schema.validate_message(
                {'type': 5,
                 'shipname': None,
                 }))

    def test_invalid_type(self):
        msg = gpsd_format.schema.get_message_default(1)
        self.assertTrue(gpsd_format.schema.validate_message(msg))
        msg['lat'] = 'foo'
        self.assertFalse(gpsd_format.schema.validate_message(msg))

    def test_valid(self):
        self.assertTrue(
            gpsd_format.schema.validate_message(
                gpsd_format.schema.get_message_default(1)))

    def test_error(self):
        self.assertFalse(gpsd_format.schema.validate_message(None))

class TestRow2Message(unittest.TestCase):

    def setUp(self):
        self.row = {
            'type': 5,
            'shipname': 'SS Test Ship',
            'shiptype': 'I fish for stuff'
        }
        self.expected = self.row.copy()
        for field in gpsd_format.schema.fields_by_message_type[self.row['type']]:
            if field not in self.row:
                self.expected[field] = gpsd_format.schema.CURRENT[field]['default']

    def test_standard(self):

        """
        Row with a valid type
        """

        actual = gpsd_format.schema.row2message(self.row)
        self.assertDictEqual(self.expected, actual)
        for field, val in self.row.items():
            self.assertEqual(actual[field], val)

    def test_drop_unrecognized_field(self):

        """
        Row with a valid type but has an unrecognized field that should be dropped
        """

        row = self.row.copy()
        row['NEW_FIELD'] = 'INVALID'
        actual = gpsd_format.schema.row2message(self.row)
        self.assertEqual(self.expected, actual)

    def test_keep_unrecognized_field(self):

        """
        Row with a valid type but has an unrecognized field that should be kept
        """

        row = self.row.copy()
        row['NEW_FIELD'] = 'KEEP'

        expected = self.expected.copy()
        expected['NEW_FIELD'] = 'KEEP'

        # Explicitly define fields
        actual = gpsd_format.schema.row2message(self.row, keep_fields=['NEW_FIELD'])
        self.assertEqual(self.expected, actual)

        # Keep all fields
        actual = gpsd_format.schema.row2message(self.row, keep_fields=True)
        self.assertEqual(self.expected, actual)

    def test_invalid_type(self):

        """
        Row with an invalid AIS message type should raise an exception
        """

        self.assertRaises(ValueError, gpsd_format.schema.row2message, {'type': ''})

class TestCastRow(unittest.TestCase):
    def test_standard(self):
        row = gpsd_format.schema.import_row({
                'type': 1,
                'shipname': 'SS Test Ship',
                'timestamp': '1970-01-02T03:04:05Z'
                })
        self.assertEqual(row['type'], 1)
        self.assertEqual(row['shipname'], 'SS Test Ship')
        self.assertEqual(row['timestamp'], datetime.datetime(1970, 1, 2, 3, 4, 5))

    def test_invalid_throw(self):
        self.assertRaises(
            Exception,
            gpsd_format.schema.import_row,
            {
                'type': '1',
                'shipname': 'SS Test Ship',
                'timestamp': 'late'
                })

    def test_invalid_convert(self):
        row = gpsd_format.schema.import_row({
                'type': 1,
                'shipname': 'SS Test Ship',
                'timestamp': 'late'
                }, throw_exceptions=False)
        self.assertEqual(row['type'], 1)
        self.assertEqual(row['shipname'], 'SS Test Ship')
        self.assertNotIn('timestamp', row)
        self.assertIn('__invalid__', row)
        self.assertIn('timestamp', row['__invalid__'])
 
class TestGetMessageDefault(unittest.TestCase):

    def test_get_default_messages(self):

        for msg_type, fields in gpsd_format.schema.fields_by_message_type.items():
            actual = gpsd_format.schema.get_message_default(msg_type)
            for field in fields:
                if field == 'type': continue
                if not gpsd_format.schema.CURRENT[field].get('required', True): continue
                self.assertIn(field, actual)
                self.assertEqual(actual[field], gpsd_format.schema.CURRENT[field]['default'])

    def test_invalid_msg_type(self):

        """
        Try to get a row for a message type that does not exist
        """

        msg_types = [None, -1, -1.23, 10000000, '', [], {}]
        for mt in msg_types:
            self.assertRaises(ValueError, gpsd_format.schema.get_message_default, mt)


class TestExportRow(unittest.TestCase):
    def test_standard(self):
        datetime_now = datetime.datetime.now()
        row = gpsd_format.schema.export_row({
                'type': 1,
                'shipname': 'SS Test Ship',
                'speed': 3.2,
                'timestamp': datetime_now
                })
        self.assertEqual(row['type'], 1)
        self.assertEqual(row['shipname'], 'SS Test Ship')
        self.assertEqual(row['speed'], 3.2)
        self.assertEqual(row['timestamp'], datetime_now.strftime(gpsd_format.schema.DATETIME_FORMAT))

    def test_invalid_throw(self):
        self.assertRaises(
            Exception,
            gpsd_format.schema.export_row,
            {
                'type': '1',
                'shipname': 'SS Test Ship',
                'timestamp': 'late'
                })

    def test_invalid_convert(self):
        row = gpsd_format.schema.export_row({
                'type': 1,
                'shipname': 'SS Test Ship',
                'timestamp': 'late'
                }, throw_exceptions=False)
        self.assertEqual(row['type'], 1)
        self.assertEqual(row['shipname'], 'SS Test Ship')
        self.assertNotIn('timestamp', row)
        self.assertIn('__invalid__', row)
        self.assertIn('timestamp', row['__invalid__'])

class TestFieldDefaults(unittest.TestCase):

    def test_field_check(self):

        """
        Make sure all default fields are defined in the schema
        """

        for fields in gpsd_format.schema.fields_by_message_type.values():
            for f in fields:
                self.assertTrue(f in gpsd_format.schema.CURRENT, msg="Field {} not found in schema".format(f))
