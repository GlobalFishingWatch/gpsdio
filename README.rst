gpsdio
======

AIS I/O with Python, dictionaries, and the `GPSd AIVDM <http://catb.org/gpsd/AIVDM.html>`_ schema.

.. image:: https://travis-ci.org/SkyTruth/gpsdio.svg?branch=master
    :target: https://travis-ci.org/SkyTruth/gpsdio


.. image:: https://coveralls.io/repos/SkyTruth/gpsdio/badge.svg?branch=master
    :target: https://coveralls.io/r/SkyTruth/gpsdio

This project is still evolving but will calm down once it hits ``v0.1``.  We
would love to hear from you're using, or would like to use, this project, both
so we don't make any unexpected changes, and to get outside opinions on AIS
processing.


Overview
--------

Vessels use a ship-to-ship Automated Identification System (AIS) to avoid
collisions by broadcasting information about who they are, where they are, and
what they are doing.  These messages are broadcast as `NMEA 0183 <https://en.wikipedia.org/wiki/NMEA_2000>`_
or `NMEA 2000 <https://en.wikipedia.org/wiki/NMEA_2000>`_ sentences and are
constantly being collected by terrestrial and satellite receivers.

NMEA is very large and difficult to work with natively, so the solution is to
parse it and store as another format.  Rather than spend time developing our
own schema we chose to adopt the `GPSd AIVDM <http://catb.org/gpsd/AIVDM.html>`_
schema, which clearly defines all message types.  Messages map well to Python
dictionaries due to how fields vary type-to-type, so that's what ``gpsdio`` uses.

This project aims to make AIS data easier to work with by providing I/O and a
small set of useful transforms, and was built with large-scale data processing
pipelines in mind.


Example I/O
-----------

Here's a small example of how to read data stored as `newline delimited JSON <https://github.com/geowurster/newlinejson>`_,
add a field, and write as GZIP compressed `MsgPack <http://msgpack.org/index.html>`_.
The driver and compression are explicitly given but can also be detected from the file path.
For more information on what ``gpsdio.open()`` returns, see the section on `messages <README.rst#Messages>`_.

.. code-block:: python

    import gpsdio

    with gpsdio.open('sample-data/types.json') as src:
        with gpsdio.open('with-num-fields.msg.gz', 'w', driver='MsgPack', compression='GZIP') as dst:
            for msg in src:
                msg['num_fields'] = len(msg)


Parsing NMEA Sentences
----------------------

``gpsdio`` does not yet support reading NMEA directly, although it will hopefully
in the near future.  In the meantime, `libais <https://github.com/schwehr/libais>`_
has an ``aisdecode`` utility with an optional ``--gpsd`` format that produces data
readable by this library.


Commandline Interface
---------------------

This project also offers a ``gpsdio`` commandline utility for common tasks like
inspecting and transforming data.  See the `CLI docs <docs/CLI.rst>`_
for more information.


Messages
--------

**NOTE:** Message validation and transformation has not quite settled and will
change for ``v0.1``.  The description below is currently mostly relevant, although
some fields may be placed into an ``__invalid__`` key on read or write.

``gpsdio.open()`` returns a file-like object called ``Stream()`` that is
responsible for taking a dictionary from the underlying driver and transforming
it into a well formed message.

Normally I/O libraries perform some strict validation while reading and before
writing data, but working with AIS usually involves adding some custom fields.
Rather than telling ``gpsdio.open()`` what additional fields it may encounter
every time a file is opened, message validation only happens when requested.
This may seem backwards, but the idea is that validation really only needs to
happen as data parsed and brought into the ``gpsdio`` world.  After that the
user knows far more about their data and is likely adding additional fields
during processing.

See `sample-data <https://github.com/SkyTruth/gpsdio/blob/master/sample-data>`_
for some data ``gpsdio`` can immediately read and write.


CLI Plugins
-----------

Developers can create their own ``gpsdio`` commands with ``click-plugins``.
``gpsdio`` loads plugins from a `setuptools entry point <https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins>`_
called ``gpsdio.cli_plugins``, so in your ``setup.py``:

.. code-block:: python

    setup(
        entry_points='''
            [gpsdio.cli_plugins]
            name=package.module:click_command
        '''
    )

For a more in-depth description see the `click-plugins <https://github.com/click-contrib/click-plugins>`_
documentation.  Additionally, see `gpsdio-density <https://github.com/SkyTruth/gpsdio-density>`_
for an example, or one of the other plugins listed in the
`plugin registry <https://github.com/SkyTruth/gpsdio/wiki/CLI-plugin-registry>`_.


Driver Plugins
--------------

External drivers should be registered to the entry-point ``gpsdio.driver_plugins`` and
must subclass ``gpsdio.base.BaseDriver`` or ``gpsdio.base.BaseCompressionDriver``.
See the docstrings on those two objects for subclassing information.


Roadmap
-------

**v0.1**

We will have reached ``v0.1`` and can confidently share this project with others.  To do that,
we need to support the syntax below.  The schema building is a little rough, but the assumption
is that users only need to do this to being non-GPSd data into gpsdio, which they should only
need to do once.  We will make this easier in the near future with a ``gpsdio-nmea-driver``.
Either way, there need to be some functions to assemble the schema.  This example brings
points with limited information into the ``GPSd`` schema:

.. code-block:: python

    import gpsdio
    from gpsdio.schema import build_schema


    # Define which fields we will see for each type
    fields_by_type = {
        1: ('mmsi', 'lat', 'lon', 'course', 'speed', 'shipname')
    }
    fields_by_type[2] = fields_by_type[1]
    fields_by_type[3] = fields_by_type[1]
    fields = {
        'type': int,
        'mmsi': int,
        'lat': float,
        'lon': float,
        'course': float,
        'speed': float,
        'shipname': str
    }
    schema = build_schema(fields_by_type, fields)


    with gpsdio.open('infile.json', schema=schema) as src, gpsdio.open('outfile.json', 'w') as dst:
        for msg in src:

            # Fill in fields not included in the message to match the destination schema
            msg = dst.fill_msg(msg)

            # Write to output file
            dst.write(msg)

* Functions to easily assemble a custom schema.
* Included schema should only define AIVDM types and _maybe_ a ``timestamp``.
* Take another pass at the driver and compression class structure, but don't let that hold up a release.
* Support experimental driver plugin registration.
* Support experimental schema extension registration.


**v1.0**

* Try pretty hard not to change the schema but if it needs to change, change it.
* Probably no dependencies that require a C compiler, except maybe an optional speedups module that re-implements some of the core I/O objects and transforms in Cython.
* Move ``MsgPack`` driver to an external project.
* ``gpsdio-nmea-driver`` for reading raw NMEA.
* GeoJSON support as an interface to GDAL.  Maybe a ``gpsdio-vector-driver``.


Installation
------------

With pip:

.. code-block:: console

    $ pip install gpsdio

From source:

.. code-block:: console

    $ git clone https://github.com/SkyTruth/gpsdio
    $ cd gpsdio
    $ python setup.py install


Developing
----------

.. code-block:: console

    $ git clone https://github.com/SkyTruth/gpsdio.git
    $ cd gpsdio
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -e .[dev]
    $ py.test tests --cov gpsdio --cov-report term-missing


Changelog
---------

See ``CHANGES.md``


License
-------

See ``LICENSE.txt``
