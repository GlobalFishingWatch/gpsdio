#!/usr/bin/python


"""
Setup script for gpsdio
"""


import os
import sys

from setuptools.command.test import test as TestCommand
from setuptools import find_packages
from setuptools import setup


# https://pytest.org/latest/goodpractises.html
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


with open('README.rst') as f:
    readme = f.read().strip()


version = None
author = None
email = None
source = None
with open(os.path.join('gpsdio', '__init__.py')) as f:
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
    author=author,
    author_email=email,
    cmdclass={'test': PyTest},
    description="A general purpose AIS I/O library using the GPSd AIVDM schema.",
    entry_points='''
        [console_scripts]
        gpsdio=gpsdio.cli:main_group

        [gpsdio.gpsdio_commands]
        cat=gpsdio.cli.cat:cat
        convert=gpsdio.cli.deprecated:convert
        env=gpsdio.cli.env:env
        etl=gpsdio.cli.etl:etl
        info=gpsdio.cli.info:info
        insp=gpsdio.cli.insp:insp
        load=gpsdio.cli.load:load
        validate=gpsdio.cli.deprecated:validate
    ''',
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
        ]
    },
    install_requires=[
        'click>=3',
        'click-plugins',
        'msgpack-python',
        'newlinejson',
        'python-dateutil',
        'str2type>=0.4',
        'six>=1.8',
        'ujson',
    ],
    license='Apache 2.0',
    long_description=readme,
    include_package_data=True,
    keywords="GPSd AIVDM AIS I/O",
    name="gpsdio",
    packages=find_packages(),
    url=source,
    version=version,
)
