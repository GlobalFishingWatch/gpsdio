import shutil
import sys
import tempfile
import unittest

import click.testing

import gpsd_format.cli


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

        main = gpsd_format.cli.main.main

        def wrapper(*arg, **kw):
            clickstderr = sys.stderr
            sys.stderr = stderr
            try:
                return main(*arg, **kw)
            finally:
                sys.stderr = clickstderr

        gpsd_format.cli.main.main = wrapper
        try:
            return self.runner.invoke(gpsd_format.cli.main, args, catch_exceptions=False)
        finally:
            gpsd_format.cli.main.main = main
