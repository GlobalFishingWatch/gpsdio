#!/usr/bin/python


"""
Setup script for gpsdio
"""


import codecs
import os

from setuptools import find_packages
from setuptools import setup


with codecs.open('README.rst', encoding='utf-8') as f:
    readme = f.read().strip()


def parse_dunder_line(string):

    """
    Take a line like:

        "__version__ = '0.0.8'"

    and turn it into a tuple:

        ('__version__', '0.0.8')

    Not very fault tolerant.
    """

    # Split the line and remove outside quotes
    variable, value = (s.strip() for s in string.split('=')[:2])
    value = value[1:-1].strip()
    return variable, value


with open(os.path.join('gpsdio', '__init__.py')) as f:
    dunders = dict((parse_dunder_line(line) for line in f if line.strip().startswith('__')))
    version = dunders['__version__']
    author = dunders['__author__']
    email = dunders['__email__']
    source = dunders['__source__']


setup(
    author=author,
    author_email=email,
    description="A general purpose AIS I/O library using the GPSd AIVDM schema.",
    entry_points='''
        [console_scripts]
        gpsdio=gpsdio.cli.main:main_group

        [gpsdio.gpsdio_commands]
        cat=gpsdio.cli.cat:cat
        env=gpsdio.cli.env:env
        etl=gpsdio.cli.etl:etl
        info=gpsdio.cli.info:info
        insp=gpsdio.cli.insp:insp
        load=gpsdio.cli.load:load
    ''',
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'coveralls'
        ]
    },
    install_requires=[
        'click>=3',
        'click-plugins',
        'msgpack-python',
        'newlinejson>=1.0',
        'str2type>=0.4',
        'six>=1.8',
        'ujson',
        'voluptuous'
    ],
    license='Apache 2.0',
    long_description=readme,
    include_package_data=True,
    keywords="AIS I/O with Python, dictionaries, and the GPSd AIVDM schema.",
    name="gpsdio",
    packages=find_packages(exclude=['test']),
    url=source,
    version=version,
)
