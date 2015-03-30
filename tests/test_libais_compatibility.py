import json
import os.path
import subprocess

from . import cmdtest

testdir = os.path.dirname(__file__)

class TestLibaisCompatibility(cmdtest.CmdTest):

    def test_no_normalize(self):

        infile = os.path.join(os.path.dirname(__file__), "types.nmea")
        outfile = os.path.join(self.dir, "out.json")

        cmd = "aisdecode --gpsd --allowUnknown --allow_missing_timestamps --encoding=json < '%s' > '%s'" % (infile, outfile)

        os.system(cmd)

        report = json.loads(self.runcmd("validate", "--print-json", "--verbose", outfile).output.split("\n")[1])

        self.assertEqual(report['num_incomplete_rows'], 0)
        self.assertEqual(report['num_invalid_rows'], 0)
