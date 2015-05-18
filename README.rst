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

Command line tools
=================

.. code-block:: console

    $ gpsd_format validate FILENAME.msg
    $ gpsd_format validate FILENAME.json
    $ gpsd_format convert FILENAME.msg FILENAME.json
    $ gpsd_format convert FILENAME.json FILENAME.msg

API
===
open
--------

.. code-block:: python
    with gpsd_format.open('infile.msg') as src:
        for msg in src:
            print msg

.. code-block:: python
    with gpsd_format.open('outfile.msg', 'w') as dst:
        dst.write(msg)

Opens a file containing gpsd format data in any of the supported container formats and optionally compressed. The returned object can be used as a context manager, and in read mode it works as an iterator over the messages in the file.

Currently supported container formats are newline delimited JSON and MsgPack and currently supported compression formats are GZIP and XZ. When possible the container format and compression types are sniffed out based on the file extensions.  These parameters can be explicitly provided via `driver` and `compression`.  Additional driver specific or compression specific options can be supplied by passing a dictionary to `do` and/or `co`.  For example, the GZIP driver uses `gzip.GzipFile()` internally so if the user wants to specify `GzipFile()`'s 'compresslevel' keyword argument they would do:

.. code-block:: python
    with gpsd_format.open('infile.msg.gz', co={'compresslevel': 9}) as src:
        for msg in src:
            pass

Additionally, some drivers and compression formats support additional modes that compliment r, w, a.  If the user wants to pass a more specific mode to a compression driver, they would do:

.. code-block:: python
    with gpsd_format.open('outfile.msg.gz', 'w', cmode='wb') as dst:
        dst.write(msg)

Simple Conversion Examples
----------------------------------------

Read from newline delimited JSON and write to GZIP compressed MsgPack:

.. code-block:: python
    import gpsd_format
    with gpsd_format.open('input.json') as src:
        with gpsd_format.open('output.msg.gz', 'w') as dst:
            for msg in src:
                dst.write(msg)

Read MsgPack compressed with GZIP and write to newline JSON with XZ compression without using file extensions:

.. code-block:: python
    import gpsd_format
    with gpsd_format.open('input', driver='msgpack', compression='gzip') as src:
        with gpsd_format.open('output', 'w', driver='newlinejson', compression='xz'):
            for msg in src:
                dst.write(msg)

Stream
-----------

A file-like object that reads, writes, and validates GPSD data. This is the type of object returned by `gpsd_format.open()`.

When reading and writing `Stream()` can perform message manipulation and validation to ensure more uniform data - there are several key flags that change how `Stream()` reads and writes data:

* `skip_failures` : Bad field values are moved to a sub-object of the message under the key '__invalid__', and any parser or validation errors are recorded under the same key instead of raising exceptions.
* `force_msg` : On read and write force the message being handled to be GPSD compliant by removing fields that do not belong and adding missing fields with default values.
* `keep_fields` : On read and write don't remove unrecognized fields. Use together with `force_msg` to only add missing fields.
* `convert` : When reading import date/time fields into an instance of `datetime.datetime` and export to a string when writing.  This can be expensive so if you can work with the dates and times as strings it is best to set this to `False`.
