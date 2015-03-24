import os.path
import cmdtest
import json

class TestGpsdCompatibility(cmdtest.CmdTest):
    def test_no_normalize(self):
        infile = os.path.join(os.path.dirname(__file__), "types.nmea")
        outfile = os.path.join(self.dir, "out.json")
        os.system("gpsdecode < '%s' > '%s'" % (infile, outfile))

        report = json.loads(self.runcmd("validate", "--print-json", "--verbose", outfile).output.split("\n")[1])

        self.assertEqual(report['num_incomplete_rows'], 0)
        self.assertEqual(report['num_invalid_rows'], 0)
