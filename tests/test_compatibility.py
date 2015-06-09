import json
import os.path
import subprocess
import urllib
import pytest

from . import cmdtest

testdir = os.path.dirname(__file__)

@pytest.mark.skipif(True, reason='gpsd library is required build from source is not fully implemented')
class TestGpsdCompatibility(cmdtest.CmdTest):
    def setUp(self):
        cmdtest.CmdTest.setUp(self)

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
