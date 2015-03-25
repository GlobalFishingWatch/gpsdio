"""
Unittests for: gpsd_format.io
"""


import os
import json
import unittest
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import gpsd_format.io
import gpsd_format.schema


VALID_ROWS = [
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 1},
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 2},
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 3},
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 4}
]

INVALID_ROWS = [
    {'type': 1, 'timestamp': 'morning'},
    {'type': 1, 'timestamp': 'late'}
]


class TestGPSDReader(unittest.TestCase):

    def setUp(self):
        self.valid_rows = [d.copy() for d in VALID_ROWS]
        self.valid_f = StringIO()
        self.valid_f.name = "valid.msg"
        gpsd_format.io.GPSDWriter(self.valid_f).writerows(self.valid_rows)
        self.valid_f.seek(0)

        self.extended_rows = []
        for row in self.valid_rows:
            row = row.copy()  # Stupid dictionary pointers ...
            row['NEW_FIELD'] = 'SOMETHING'
            self.extended_rows.append(row)
        self.extended_f = StringIO()
        self.extended_f.name = "extended.msg"
        gpsd_format.io.GPSDWriter(self.extended_f).writerows(self.extended_rows)
        self.extended_f.seek(0)

        self.invalid_f = StringIO()
        self.invalid_f.name = "invalid.msg"
        gpsd_format.io.GPSDWriter(self.invalid_f).writerows(VALID_ROWS)
        self.invalid_f.write("N")
        gpsd_format.io.GPSDWriter(self.invalid_f, force_message=False, convert=False).writerows(INVALID_ROWS)
        self.invalid_f.seek(0)

    def tearDown(self):
        self.valid_f.close()
        self.extended_f.close()
        self.invalid_f.close()

    def test_context(self):
        with gpsd_format.io.GPSDReader(self.valid_f, force_message=False, keep_fields=True) as r:
            self.assertFalse(r.closed)

    def test_no_normalize(self):

        """
        Just read newline JSON - don't do any validation or casting
        """

        reader = gpsd_format.io.GPSDReader(self.valid_f, force_message=False, keep_fields=True)
        for expected, actual in zip(self.valid_rows, reader):
            self.assertDictEqual(expected, actual)

    def test_keep_invalid_fields(self):

        """
        Read newline JSON with invalid AIS fields but keep the fields
        """

        reader = gpsd_format.io.GPSDReader(self.extended_f, force_message=False, keep_fields=True)
        for expected, actual in zip(self.extended_rows, reader):
            self.assertDictEqual(expected, actual)

    def test_drop_invalid_fields(self):

        """
        Read newline JSON with invalid AIS fields but drop the unrecognized fields
        """

        reader = gpsd_format.io.GPSDReader(self.extended_f, force_message=False, keep_fields=False)
        for expected, actual in zip(self.extended_rows, reader):
            self.assertDictEqual(expected, actual)

    def test_force_message_drop_invalid(self):

        """
        Read newline JSON with invalid AIS fields - each row is forced to be
        a valid AIS message type and the unrecognized fields are dropped
        """

        reader = gpsd_format.io.GPSDReader(self.extended_f, force_message=True, keep_fields=False)
        for invalid_row, actual_row in zip(self.extended_rows, reader):
            expected_row = gpsd_format.schema.get_message_default(actual_row['type'])
            expected_row.update({key: val for key, val in invalid_row.items() if key in expected_row})
            self.assertDictEqual(expected_row, actual_row)

    def test_force_message_keep_invalid(self):

        """
        Read newline JSON with invalid AIS fields - each row is forced to be
        a valid AIS message type and the unrecognized fields are kept
        """

        reader = gpsd_format.io.GPSDReader(self.extended_f, force_message=True, keep_fields=True)
        for invalid_row, actual_row in zip(self.extended_rows, reader):
            expected_row = gpsd_format.schema.get_message_default(actual_row['type'])
            expected_row.update(invalid_row)
            self.assertDictEqual(expected_row, actual_row)

    def test_throw_exceptions(self):
        f = StringIO("nananan\n")
        f.name = "exception.msg"
        reader = gpsd_format.io.GPSDReader(f, force_message=True, keep_fields=True, throw_exceptions=True)
        self.assertRaises(Exception, reader.next)
        reader.close()

    def test_survive_anything(self):
        reader = gpsd_format.io.GPSDReader(self.invalid_f, force_message=True, keep_fields=True, throw_exceptions=False)
        bad_lines = 0
        bad_fields = 0
        for row in reader:
            if '__invalid__' in row:
                if '__content__' in row['__invalid__']:
                    bad_lines += 1
                else:
                    bad_fields += 1
        self.assertEqual(bad_lines, 1)
        self.assertEqual(bad_fields, 2)


class TestGPSDWriter(unittest.TestCase):

    def setUp(self):

        global VALID_ROWS

        self.valid_rows = [d.copy() for d in VALID_ROWS]
        self.valid_f = StringIO(os.linesep.join([json.dumps(row) for row in self.valid_rows]))

        self.extended_rows = []
        for row in self.valid_rows:
            row = row.copy()  # Stupid dictionary pointers ...
            row['NEW_FIELD'] = 'SOMETHING'
            self.extended_rows.append(row)
        self.extended_f = StringIO(os.linesep.join([json.dumps(row) for row in self.extended_rows]))

    def tearDown(self):
        self.valid_f.close()
        self.extended_f.close()

    def test_context(self):
        test_f = StringIO()
        with gpsd_format.io.GPSDWriter(test_f, force_message=False, keep_fields=True) as w:
            self.assertFalse(w.closed)

    def test_compatibility(self):
        test_f = StringIO()
        w = gpsd_format.io.GPSDWriter(test_f, force_message=False, keep_fields=True)
        w.writeheader()
        w.close()

    def test_no_normalize(self):

        """
        Just write and read newline JSON - don't do any validation or casting
        """

        test_f = StringIO()
        writer = gpsd_format.io.GPSDWriter(test_f, force_message=False, keep_fields=True)
        writer.writerows(self.extended_rows)

        test_f.seek(0)
        reader = gpsd_format.io.GPSDReader(test_f, force_message=False, keep_fields=True)

        for expected, actual in zip(self.extended_rows, reader):
            self.assertDictEqual(expected, actual)

    def test_drop_invalid_fields(self):

        """
        Write newline JSON with invalid AIS fields but drop the unrecognized fields
        """

        test_f = StringIO()
        writer = gpsd_format.io.GPSDWriter(test_f, force_message=False, keep_fields=False)

        for line in self.extended_rows:
            writer.writerow(line)

        test_f.seek(0)
        reader = gpsd_format.io.GPSDReader(test_f, force_message=False, keep_fields=True)

        for expected, actual in zip(self.valid_rows, reader):
            self.assertDictEqual(expected, actual)

    def test_force_message_drop_invalid(self):

        """
        Write newline JSON with invalid AIS fields - each row is forced to be
        a valid AIS message type and the unrecognized fields are dropped
        """

        test_f = StringIO()
        writer = gpsd_format.io.GPSDWriter(test_f, force_message=True, keep_fields=False)

        for line in self.extended_rows:
            try:
                writer.writerow(line)
            except:
                raise

        test_f.seek(0)
        reader = gpsd_format.io.GPSDReader(test_f, force_message=False, keep_fields=True)

        for expected, actual in zip([gpsd_format.schema.row2message(gpsd_format.schema.import_row(row.copy()))
                                     for row in self.valid_rows], reader):
            self.assertDictEqual(expected, actual)

    def test_force_message_keep_invalid(self):

        """
        Write newline JSON with invalid AIS fields - each row is forced to be
        a valid AIS message type and the unrecognized fields are kept
        """

        test_f = StringIO()
        writer = gpsd_format.io.GPSDWriter(test_f, force_message=True, keep_fields=True)

        for line in self.extended_rows:
            writer.writerow(line)

        test_f.seek(0)
        reader = gpsd_format.io.GPSDReader(test_f, force_message=False, keep_fields=True)

        for expected, actual in zip([gpsd_format.schema.row2message(gpsd_format.schema.import_row(row.copy()), keep_fields=True)
                                     for row in self.extended_rows], reader):
            self.assertDictEqual(expected, actual)
