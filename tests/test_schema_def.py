"""
Unittests for: gpsd_format._schema_def
"""


import datetime
import unittest

import gpsd_format.schema
import gpsd_format._schema_def


class TestDatetime2Str(unittest.TestCase):

    def test_standard(self):

        """
        Convert a datetime object to a string
        """

        now = datetime.datetime.now()

        # Manually export datetime to the expected string format
        expected_string = now.strftime(gpsd_format.schema.DATETIME_FORMAT)

        # Convert the datetime object to a string with the function
        converted = gpsd_format._schema_def.datetime2str(now)
        self.assertEqual(expected_string, converted)

        # Reload the string with datetime and make sure everything matches
        reloaded = datetime.datetime.strptime(converted, gpsd_format.schema.DATETIME_FORMAT)
        self.assertEqual(now.year, reloaded.year)
        self.assertEqual(now.month, reloaded.month)
        self.assertEqual(now.day, reloaded.day)
        self.assertEqual(now.hour, reloaded.hour)
        self.assertEqual(now.second, reloaded.second)
        self.assertEqual(now.microsecond, reloaded.microsecond)
        self.assertEqual(now.tzinfo, reloaded.tzinfo)


class TestStr2Datetime(unittest.TestCase):

    def test_standard(self):

        """
        Convert a standard datetime string to a datetime object
        """

        string = '2014-12-19T15:29:36.479005Z'
        expected = datetime.datetime.strptime(string, gpsd_format.schema.DATETIME_FORMAT)
        converted = gpsd_format._schema_def.str2datetime(string)
        self.assertEqual(string, converted.strftime(gpsd_format.schema.DATETIME_FORMAT))

        self.assertEqual(expected.year, converted.year)
        self.assertEqual(expected.month, converted.month)
        self.assertEqual(expected.day, converted.day)
        self.assertEqual(expected.hour, converted.hour)
        self.assertEqual(expected.second, converted.second)
        self.assertEqual(expected.tzinfo, converted.tzinfo)
