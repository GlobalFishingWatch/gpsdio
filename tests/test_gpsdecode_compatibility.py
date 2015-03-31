import json
import os.path
import subprocess

from . import cmdtest

testdir = os.path.dirname(__file__)

class TestGpsdCompatibility(cmdtest.CmdTest):
    def setUp(self):
        cmdtest.CmdTest.setUp(self)

        self.utilsdir = os.path.join(testdir, "..", "utils")
        cmd = [os.path.join(self.utilsdir, "install-latest-gpsd")]
        self.gpsddir = subprocess.check_output(cmd, cwd=self.utilsdir).strip()


    def test_known_types(self):
        infile = os.path.join(os.path.dirname(__file__), "types.nmea")
        outfile = os.path.join(self.dir, "out.json")

        cmd = "LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:%s\" %s/gpsdecode < '%s' > '%s'" % (self.gpsddir, self.gpsddir, infile, outfile)

        os.system(cmd)

        report = json.loads(self.runcmd("validate", "--print-json", "--verbose", outfile).output.split("\n")[1])

        self.assertEqual(report['num_incomplete_rows'], 0)
        self.assertEqual(report['num_invalid_rows'], 0)

    def test_samples_from_gpsd(self):
        infile = os.path.join(self.gpsddir, "test", "sample.aivdm")
        outfile = os.path.join(self.dir, "out.json")

        cmd = "LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:%s\" %s/gpsdecode < '%s' > '%s'" % (self.gpsddir, self.gpsddir, infile, outfile)

        os.system(cmd)

        report = json.loads(self.runcmd("validate", "--print-json", "--verbose", outfile).output.split("\n")[1])

        self.assertEqual(report['num_incomplete_rows'], 0)
        self.assertEqual(report['num_invalid_rows'], 0)
