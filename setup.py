#! /usr/bin/python


from setuptools import setup


with open('requirements.txt') as f:
    install_requires = f.read().strip()


version = None
author = None
email = None
source = None
with open('gpsd_format/__init__.py') as f:
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
    name="gpsd_format",
    description="A library and command line tool to read, write and validate "
                "AIS and GPS messages in the GPSD JSON format (or the same format in a msgpack container).",
    keywords="gpsd",
    # install_requires=["python-dateutil"],
    # extras_require={
    #     'cli': ["click>=3.3"],
    #     'msgpack': ["msgpack-python>=0.4.2"],
    #     'test': ["nose", "coverage"]
    # },
    version="0.0.2",
    author="Egil Moeller, Kevin Wurster",
    author_email="egil@skytruth.org, kevin@skytruth.org",
    license="GPL",
    url="https://github.com/SkyTruth/gpsd_format",
    include_package_data=True,
    install_requires=install_requires,
    packages=['gpsd_format'],
    entry_points='''
        [console_scripts]
        gpsd_format=gpsd_format.cli:main
    '''
)
