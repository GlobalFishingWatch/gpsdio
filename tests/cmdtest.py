import unittest
import tempfile
import click.testing
import shutil
import gpsd_format.cli


class CmdTest(unittest.TestCase):
    keep_tree = False

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.runner = click.testing.CliRunner()
        if self.keep_tree:
            print "CmdTest is running in %s" % self.dir

    def tearDown(self):
        if not self.keep_tree:
            shutil.rmtree(self.dir)

    def runcmd(self, *args):
        return self.runner.invoke(gpsd_format.cli.main, args, catch_exceptions=False)
