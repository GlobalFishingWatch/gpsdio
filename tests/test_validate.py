"""
Unittests for: `gpsdio.validate`
"""


import datetime
import json
import os.path
import random
import sys
import unittest

from click.testing import CliRunner
import six

from . import cmdtest
import gpsdio
import gpsdio.cli
import gpsdio.schema
import gpsdio.validate


class TestInfoDetails(cmdtest.CmdTest):

    def test_extend(self):
        data = {"foo": 1}
        self.assertDictEqual(data, gpsdio.validate.merge_info({}, data))
        d1 = {
            'num_rows': 3,
            'num_incomplete_rows': 1,
            'num_invalid_rows': 2,
            'lat_min': 5,
            'lat_max': 7,
            'lon_min': 11,
            'lon_max': 13,
            'min_timestamp': datetime.datetime(1970, 1, 2, 0, 0, 0),
            'max_timestamp': datetime.datetime(1971, 3, 4, 5, 6, 7),
            'is_sorted': True,
            'is_sorted_files': True,
            'mmsi_declaration': True,
            'mmsi_hist': {
                '111111111': 1,
                '222222222': 2,
            },
            'msg_type_hist': {
                1: 1,
                2: 2
            }
        }

        d2 = {
            'num_rows': 5,
            'num_incomplete_rows': 2,
            'num_invalid_rows': 3,
            'lat_min': 6,
            'lat_max': 8,
            'lon_min': 10,
            'lon_max': 12,
            'min_timestamp': datetime.datetime(1970, 1, 1, 0, 0, 0),
            'max_timestamp': datetime.datetime(1971, 2, 1, 0, 0, 0),
            'is_sorted': True,
            'is_sorted_files': True,
            'mmsi_declaration': True,
            'mmsi_hist': {
                '111111111': 1,
                '333333333': 4,
            },
            'msg_type_hist': {
                1: 4,
                3: 1
            }
        }

        expected = {
            'is_sorted': True,
            'is_sorted_files': False,
            'lat_max': 8,
            'lat_min': 5,
            'lon_max': 13,
            'lon_min': 10,
            'max_timestamp': datetime.datetime(1971, 3, 4, 5, 6, 7),
            'min_timestamp': datetime.datetime(1970, 1, 1, 0, 0),
            'mmsi_declaration': True,
            'mmsi_hist': {'111111111': 2, '222222222': 2, '333333333': 4},
            'msg_type_hist': {1: 5, 2: 2, 3: 1},
            'num_incomplete_rows': 3,
            'num_invalid_rows': 5,
            'num_rows': 8
            }

        self.assertDictEqual(expected, gpsdio.validate.merge_info(d1, d2))


class TestInfo(cmdtest.CmdTest):

    keep_tree = True
    maxDiff = None
    epoch = datetime.datetime(1970, 1, 1)

    def _random_row(self):
        msg_types = list(gpsdio.schema.fields_by_msg_type.keys())
        msg_type = msg_types[random.randint(0, len(msg_types) - 1)]

        return {
            'lon': random.uniform(-180, 180),
            'lat': random.uniform(-90, 90),
            'timestamp': datetime.datetime.fromtimestamp(
                random.randint(0, int((datetime.datetime.now() - self.epoch).total_seconds()))),
            'mmsi': random.randint(100000000, 100000010),
            'type': msg_type  # TODO: FIXME: Support all types eventually: random.randint(1, 32)
        }

    num_rows = 2
    num_invalid_rows = 1

    def setUp(self):
        cmdtest.CmdTest.setUp(self)

        # The result of _random_row has a random timestamp so this value must be overwritten when the list of rows
        # to test is computed.  Every iteration picks a new time between the last time and now.
        self.rows = []
        previous_timestamp = self.epoch
        for row in [self._random_row() for r in range(self.num_rows)]:
            now = datetime.datetime.now()
            # Since it takes far less than a second to create this set of tests rows it is possible for one of the
            # new timestamps created below to be the exact same (in seconds) as the previous timestamp.  The while
            # statement prevents that from happening
            while now == previous_timestamp:
                now = datetime.datetime.now()
            new_timestamp = datetime.datetime.utcfromtimestamp(random.randint(
                int((previous_timestamp - self.epoch).total_seconds()), int((now - self.epoch).total_seconds())))
            row['timestamp'] = new_timestamp
            previous_timestamp = new_timestamp
            self.rows.append(row)

        self.expected = {
            u'num_rows': self.num_rows + self.num_invalid_rows,
            u'num_incomplete_rows': self.num_rows,
            u'num_invalid_rows': self.num_invalid_rows,  # None of the input rows are complete messages
            u'lat_min': min([r['lat'] for r in self.rows]),
            u'lat_max': max([r['lat'] for r in self.rows]),
            u'lon_min': min([r['lon'] for r in self.rows]),
            u'lon_max': max([r['lon'] for r in self.rows]),
            u'min_timestamp': str(min([r['timestamp'] for r in self.rows]).strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
            u'max_timestamp': str(max([r['timestamp'] for r in self.rows]).strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
            u'mmsi_hist': {},
            u'msg_type_hist': {},
            u'is_sorted': True,
            u'is_sorted_files': True,
            u'mmsi_declaration': False
        }
        for row in self.rows:
            mmsi = str(row['mmsi'])
            if mmsi in self.expected['mmsi_hist']:
                self.expected[u'mmsi_hist'][mmsi] += 1
            else:
                self.expected[u'mmsi_hist'][mmsi] = 1

            msgtype = str(row['type'])
            if msgtype in self.expected['msg_type_hist']:
                self.expected[u'msg_type_hist'][msgtype] += 1
            else:
                self.expected[u'msg_type_hist'][msgtype] = 1

    def test_sorted(self):
        infile = os.path.join(self.dir, "rows.mmsi=123.msg")
        with open(infile, "w") as f:
            w = gpsdio.open(f, 'w')
            for row in self.rows:
                w.write(row)
            for x in six.moves.range(0, self.num_invalid_rows):
                f.write("N")

        self.expected[u'file'] = str(infile)

        result = CliRunner().invoke(gpsdio.cli.main_group, [
            'validate',
            '--print-json',
            infile
        ])
        self.assertEqual(result.exit_code, 0)

        actual = json.loads(result.output)
        self.assertDictEqual(json.loads(json.dumps(self.expected)), actual)

    def test_unsorted(self):
        self.rows[0:2] = [self.rows[1], self.rows[0]]
        infile = os.path.join(self.dir, "rows.mmsi=123.msg")
        with open(infile, "w") as f:
            w = gpsdio.open(f, 'w')
            for row in self.rows:
                w.write(row)
            for x in six.moves.range(0, self.num_invalid_rows):
                f.write("N")

        self.expected[u'file'] = str(infile)
        self.expected['is_sorted'] = False

        result = CliRunner().invoke(gpsdio.cli.main_group, [
            'validate',
            '--print-json',
            infile
        ])
        self.assertEqual(result.exit_code, 0)

        actual = json.loads(result.output)
        self.assertDictEqual(self.expected, actual)

    def test_nonjson(self):
        infile = os.path.join(self.dir, "rows.mmsi=123.msg")
        with open(infile, "w") as f:
            w = gpsdio.open(f, 'w')
            for row in self.rows:
                w.write(row)
            for x in six.moves.range(0, self.num_invalid_rows):
                f.write("N\n")

        out = self.runcmd("validate", "--verbose", "--msg-hist", "--mmsi-hist", infile).output

        self.assertIn("All rows are sorted: True", out)
        self.assertIn("->", out)


class TestValidateMessage(unittest.TestCase):

    def test_all_types(self):
        for msg_type, msg_fields in gpsdio.schema.fields_by_msg_type.items():

            # Check type field individually since the other tests force it to be correct
            assert not gpsdio.schema.validate_msg({'field': 'val'})

            for value in gpsdio.schema.CURRENT['type']['bad']:
                assert not gpsdio.schema.validate_msg(
                    {'type': value})

            # Construct a good message
            num_alterantives = max(*[len(gpsdio.schema.CURRENT[f]['good'])
                                     for f in msg_fields
                                     if f != 'type' and 'good' in gpsdio.schema.CURRENT[f]])

            for alt in xrange(0, num_alterantives):
                good_message = gpsdio.schema.get_default_msg(int(msg_type))
                good_message.update({f: gpsdio.schema.CURRENT[f]['good'][alt]
                                     for f in msg_fields
                                     if f != 'type' and 'good' in gpsdio.schema.CURRENT[f] and len(gpsdio.schema.CURRENT[f]['good']) > alt})

                assert gpsdio.schema.validate_msg(good_message), \
                    "Supposed 'good' msg failed validation: %s" % good_message

            # Creating a bad message from all of the bad values is an insufficient test because the validator
            # will start checking fields and as soon as it gets to a bad one it will flag the message as invalid.
            # Every field is checked in every message and every bad field is logged but we can't validate individual
            # fields without taking a good message and then changing one field at a time to a bad field.
            for field in msg_fields:
                if field != 'type' 'bad' in gpsdio.schema.CURRENT[field]:
                    for value in gpsdio.schema.CURRENT[field]['bad']:
                        bad_message = good_message.copy()
                        bad_message[field] = value
                        assert not gpsdio.schema.validate_msg(bad_message), \
                            "Field `%s' should have caused message to fail: %s" % (field, bad_message)
