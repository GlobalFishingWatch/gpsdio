#! /usr/bin/python


"""
Setup script for gpsdio
"""


import sys

from setuptools.command.test import test as TestCommand
from setuptools import find_packages
from setuptools import setup


# and https://pytest.org/latest/goodpractises.html
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


version = None
author = None
email = None
source = None
with open('gpsdio/__init__.py') as f:
    for line in f:
        if line.strip().startswith('__version__'):
            version = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__author__'):
            author = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__email__'):
            email = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__source__'):
            source = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif None not in (version, author, email, source):
            break


setup(
    name="gpsdio",
    cmdclass={'test': PyTest},
    description="A library and command line tool to read, write and validate "
                "AIS and GPS messages in the GPSD JSON format (or the same format in a msgpack container).",
    keywords="gpsd",
    install_requires=[
        'click',
        'msgpack-python',
        'newlinejson',
        'python-dateutil',
        'six',
        'ujson',
        'cligj>=0.2',
        'str2type>=0.4'
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-cov',
        ]
    },
    version=version,
    author=author,
    author_email=email,
    license="GPL",
    url=source,
    include_package_data=True,
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        gpsdio=gpsdio.cli:main_group

        [gpsdio.gpsdio_commands]
        cat=gpsdio.cli.commands:cat
        convert=gpsdio.cli.commands:convert
        env=gpsdio.cli.commands:env
        etl=gpsdio.cli.commands:etl
        insp=gpsdio.cli.commands:insp
        load=gpsdio.cli.commands:load
        validate=gpsdio.cli.commands:validate
    '''
)
