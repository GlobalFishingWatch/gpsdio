Package Layout
==============

* GPSD Format
    - gpsdio
        + __init__.py
        + drivers.py
        + io.py
        + cli.py
        + validate.py
        + schema.py
        + _schema_def.py
    - LICENSE.txt
    - MANIFEST.in
    - tests
        + __init__.py
        + test_drivers.py
        + test_io.py
        + test_cli.py
        + test_validate.py
        + test_schema.py
        + test__schema_def.py
    - setup.py


Drivers
=======

* Initial supported formats
    - MsgPack
    - Newline delmited JSON
* Potential additions
    - JSON (as a list)
    - CSV (?)
    - NMEA (via libais)
    - Vectors via fiona?
* Requirements
    - Operate on a file stream
    - Writers should have .write() function
    - Do not perform any validation


API Examples
============

.. code-block:: python

    import gpsdio

    # Print all messages in a file
    with gpsdio.open("foo.msg", skip_faliures=True) as f:
        for msg in f:
            print(msg)

    # Write two messages to a file as MsgPack
    with gpsdio.open("bar.msg", 'w', skip_failures=True) as f:
        f.write({'type': 1, 'lat': 47, 'lon': 11})
        f.write({'type': 1, 'lat': 48, 'lon': 12})

    # Validate a message
    msg = {'type': 1, 'lat': 'nanananana'}
    if gpsdio.schema.validate_msg(msg, skip_failures=True):
        print "Is valid"
    else:
        print "Is invalid", msg['__invalid__']
    
    # Get info about a collection of messages
    with gpsdio.open("foo.msg", skip_failures=False, force_message=False) as f:
        print(gpsdio.schema.collect_info(f))
