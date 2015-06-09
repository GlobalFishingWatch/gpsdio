GPSD Format
===========


.. image:: https://travis-ci.org/SkyTruth/gpsdio.svg?branch=master
    :target: https://travis-ci.org/SkyTruth/gpsdio


.. image:: https://coveralls.io/repos/SkyTruth/gpsdio/badge.svg?branch=master
    :target: https://coveralls.io/r/SkyTruth/gpsdio


A collection of tools for working with the GPSD JSON format (or the same format in a msgpack container).

Currently only a subset of message types are supported.

* A library to read and write messages in the format
* A command line tool to validate files in the format and give feedback on statistics and any errors found


CLI Plugins
-----------

The ``gpsdio`` commandline utility supports loading plugins via `setuptools entry points <https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins>`_.
Plugins should must be a `click <http://click.pocoo.org/4/>`_ command or group and should be
registered to a ``gpsdio.gpsdio_plugins`` entry point.  An example plugin is `gpsdio-density <https://github.com/SkyTruth/gpsdio-density>`_
which generates density rasters from positional AIS messages.

Plugins also have access to information from the global click context.  Since
multiple commands care about things like input and output drivers, compression,
options, and verbosity, this information is available to plugin commands that are
decorated with ``@click.pass_context`` through a dictionary stored in ``ctx.obj``.

The objects available in ``ctx.obj`` that will not change are as follows:

* ``i_drv : str`` - Driver name for input file.
* ``i_drv_opts : dict`` - A dictionary for ``do`` in ``gpsdio.open()``.  Values have already been decoded to their Python type, including JSON.
* ``i_cmp : str`` - Compression driver name for input file.
* ``i_cmp_opts : dict`` - Same idea as ``i_drv_opts``.

Output options are the same after swapping ``i_`` for ``o_``.


Drivers
-------

External drivers should be registered to the entry-point ``gpsdio.drivers``.


Installation
------------

.. code-block:: console

    $ pip install https://github.com/skytruth/gpsdio


Developing
----------

.. code-block:: console

    $ git clone https://github.com/SkyTruth/gpsdio.git
    $ cd gpsdio
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -e .[test]
    $ py.test tests --cov gpsdio --cov-report term-missing


Command line tools
------------------

.. code-block:: console

    $ gpsdio validate FILENAME.msg
    $ gpsdio validate FILENAME.json
    $ gpsdio convert FILENAME.msg FILENAME.json
    $ gpsdio convert FILENAME.json FILENAME.msg


API
---

Opening a file:

.. code-block:: python

    with gpsdio.open('infile.msg') as src:
        for msg in src:
            print msg

.. code-block:: python

    with gpsdio.open('outfile.msg', 'w') as dst:
        dst.write(msg)

Opens a file containing gpsd format data in any of the supported container formats and optionally compressed. The returned object can be used as a context manager, and in read mode it works as an iterator over the messages in the file.

Currently supported container formats are newline delimited JSON and MsgPack and currently supported compression formats are GZIP and XZ. When possible the container format and compression types are sniffed out based on the file extensions.  These parameters can be explicitly provided via `driver` and `compression`.  Additional driver specific or compression specific options can be supplied by passing a dictionary to `do` and/or `co`.  For example, the GZIP driver uses `gzip.GzipFile()` internally so if the user wants to specify `GzipFile()`'s 'compresslevel' keyword argument they would do:

.. code-block:: python

    with gpsdio.open('infile.msg.gz', co={'compresslevel': 9}) as src:
        for msg in src:
            pass

Additionally, some drivers and compression formats support additional modes that compliment r, w, a.  If the user wants to pass a more specific mode to a compression driver, they would do:

.. code-block:: python

    with gpsdio.open('outfile.msg.gz', 'w', cmode='wb') as dst:
        dst.write(msg)


Simple Conversion Examples
--------------------------

Read from newline delimited JSON and write to GZIP compressed MsgPack:

.. code-block:: python

    import gpsdio
    with gpsdio.open('input.json') as src:
        with gpsdio.open('output.msg.gz', 'w') as dst:
            for msg in src:
                dst.write(msg)

Read MsgPack compressed with GZIP and write to newline JSON with XZ compression without using file extensions:

.. code-block:: python

    import gpsdio
    with gpsdio.open('input', driver='msgpack', compression='gzip') as src:
        with gpsdio.open('output', 'w', driver='newlinejson', compression='xz'):
            for msg in src:
                dst.write(msg)

Stream
------

A file-like object that reads, writes, and validates GPSD data. This is the type of object returned by ``gpsdio.open()``.

When reading and writing ``Stream()`` can perform message manipulation and validation to ensure more uniform data - there are several key flags that change how ``Stream()`` reads and writes data:

* ``skip_failures`` : Bad field values are moved to a sub-object of the message under the key '__invalid__', and any parser or validation errors are recorded under the same key instead of raising exceptions.
* ``force_msg`` : On read and write force the message being handled to be GPSD compliant by removing fields that do not belong and adding missing fields with default values.
* ``keep_fields`` : On read and write don't remove unrecognized fields. Use together with ``force_msg`` to only add missing fields.
* ``convert`` : When reading import date/time fields into an instance of ``datetime.datetime`` and export to a string when writing.  This can be expensive so if you can work with the dates and times as strings it is best to set this to `False`.
