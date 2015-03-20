#! /usr/bin/python

from setuptools.command import easy_install
from setuptools import setup, find_packages
import shutil
import os.path
import sys
import hashlib

setup(
    name = "gpsd_format",
    description = "A library and command line tool to read, write and validate AIS and GPS messages in the GPSD JSON format (or the same format in a msgpack container).",
    keywords = "gpsd",
    install_requires = ["python-dateutil"],
    extras_require = {
        'cli':  ["click>=3.3"],
        'msgpack':  ["msgpack-python>=0.4.2"],
        'test': ["nose", "coverage"]
    },
    version = "0.0.1",
    author = "Egil Moeller",
    author_email = "egil@skytruth.org",
    license = "GPL",
    url = "https://github.com/SkyTruth/gpsd_format",
    packages=[
        'gpsd_format',
    ],
    entry_points='''
        [console_scripts]
        gpsd_format=gpsd_format.cli:main
    '''
)
