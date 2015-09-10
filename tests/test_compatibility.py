"""
Test against other decoders
"""


# TODO: Do we want this in gpsdio?


import json
import os.path
import subprocess
import shutil
import sys
import tempfile
import unittest
import urllib

import pytest

import click.testing

import gpsdio.cli
import gpsdio.cli.main


testdir = os.path.dirname(__file__)


class CmdTest(unittest.TestCase):
    keep_tree = False

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.runner = click.testing.CliRunner()
        if self.keep_tree:
            print("CmdTest is running in %s" % self.dir)

    def tearDown(self):
        if not self.keep_tree:
            shutil.rmtree(self.dir)

    def runcmd(self, *args):
        stderr = sys.stderr

        main = gpsdio.cli.main.main_group

        # def wrapper(*arg, **kw):
        #     clickstderr = sys.stderr
        #     sys.stderr = stderr
        #     try:
        #         return main(*arg, **kw)
        #     finally:
        #         sys.stderr = clickstderr
        # gpsdio.cli.main_group = wrapper

        try:
            return self.runner.invoke(gpsdio.cli.main.main_group, args, catch_exceptions=False)
        finally:
            gpsdio.cli.main_group = main


@pytest.mark.skipif(
    True, reason='gpsd library is required build from source is not fully implemented')
class TestGpsdCompatibility(CmdTest):
    def setUp(self):
        CmdTest.setUp(self)

        self.utilsdir = os.path.join(testdir, "..", "utils")
        cmd = [os.path.join(self.utilsdir, "install-latest-gpsd")]
        self.gpsddir = subprocess.check_output(cmd, cwd=self.utilsdir).strip()

    def download(self, filename, url):
        with open(os.path.join(self.dir, filename), "w") as outf:
            inf = urllib.urlopen(url)
            outf.write(inf.read())
            inf.close()
        
    def validate_file(self, infile, parser):
        outfile = os.path.join(self.dir, "out.json")

        if parser == 'gpsdecode':
            cmd = "LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:%s\" %s/gpsdecode < '%s' > '%s'" % (self.gpsddir, self.gpsddir, infile, outfile)
        elif parser == 'aisdecode':
            cmd = "aisdecode --gpsd --allowUnknown --allow_missing_timestamps --encoding=json < '%s' > '%s'" % (infile, outfile)

        os.system(cmd)

        report = json.loads(self.runcmd("validate", "--print-json", "--verbose", outfile).output)

        self.assertEqual(report['num_invalid_rows'], 0)
        self.assertEqual(report['num_incomplete_rows'], 0)

    def test_gpsdecode_known_types(self):
        self.validate_file(os.path.join(os.path.dirname(__file__), "types.nmea"), 'gpsdecode')

    def test_gpsdecode_samples_from_gpsd(self):
        self.download("gpsd.nmea", "http://git.savannah.gnu.org/cgit/gpsd.git/plain/test/sample.aivdm")
        self.validate_file(os.path.join(self.dir, "gpsd.nmea"), 'gpsdecode')

    def test_gpsdecode_samples_from_libais(self):
        self.download("libais.nmea", "https://raw.githubusercontent.com/schwehr/libais/master/test/typeexamples.nmea")
        self.validate_file(os.path.join(self.dir, "libais.nmea"), 'gpsdecode')

    def test_aisdecode_known_types(self):
        self.validate_file(os.path.join(os.path.dirname(__file__), "types.nmea"), 'aisdecode')

    def test_aisdecode_samples_from_gpsd(self):
        self.download("gpsd.nmea", "http://git.savannah.gnu.org/cgit/gpsd.git/plain/test/sample.aivdm")
        self.validate_file(os.path.join(self.dir, "gpsd.nmea"), 'aisdecode')

    def test_aisdecode_samples_from_libais(self):
        self.download("libais.nmea", "https://raw.githubusercontent.com/schwehr/libais/master/test/typeexamples.nmea")
        self.validate_file(os.path.join(self.dir, "libais.nmea"), 'aisdecode')
