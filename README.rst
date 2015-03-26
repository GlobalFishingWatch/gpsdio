===========
GPSD Format
===========


.. image:: https://travis-ci.org/SkyTruth/gpsd_format.svg?branch=master
    :target: https://travis-ci.org/SkyTruth/gpsd_format


.. image:: https://coveralls.io/repos/SkyTruth/gpsd_format/badge.svg?branch=master
    :target: https://coveralls.io/r/SkyTruth/gpsd_format


A collection of tools for working with the GPSD JSON format (or the same format in a msgpack container).

Currently only a subset of message types are supported.

* A library to read and write messages in the format
* A command line tool to validate files in the format and give feedback on statistics and any errors found


Installation
============

.. code-block:: console

    $ pip install https://github.com/skytruth/gpsd_format


Developing
==========

.. code-block:: console

    $ git clone https://github.com/SkyTruth/gpsd_format.git
    $ cd gpsd_format
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -e .
    $ nosetests --with-coverage
