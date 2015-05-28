#! /usr/bin/python


from setuptools import setup
from setuptools.command.test import test as TestCommand


# From http://fgimian.github.io/blog/2014/04/27/running-nose-tests-with-plugins-using-the-python-setuptools-test-command/
# and https://pytest.org/latest/goodpractises.html
class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests'])



with open('requirements.txt') as f:
    install_requires = f.read().strip()


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
    cmdclass={'test': NoseTestCommand},
    description="A library and command line tool to read, write and validate "
                "AIS and GPS messages in the GPSD JSON format (or the same format in a msgpack container).",
    keywords="gpsd",
    # install_requires=["python-dateutil"],
    # extras_require={
    #     'cli': ["click>=3.3"],
    #     'msgpack': ["msgpack-python>=0.4.2"],
    #     'test': ["nose", "coverage"]
    # },
    version=version,
    author=author,
    author_email=email,
    license="GPL",
    url=source,
    include_package_data=True,
    install_requires=install_requires,
    packages=['gpsdio'],
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
