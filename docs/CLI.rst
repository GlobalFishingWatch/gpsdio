Command Line Interface
======================

The ``gpsdio`` utility offers access to several common AIS operations.  This
project is still evolving so several flags and commands have been deprecated.
They still appear in the actual CLI but references have been removed from this
document.  For more information about a specific command, see ``gpsdio $CMD --help``.

.. code-block:: console

    Usage: gpsdio [OPTIONS] COMMAND [ARGS]...

      gpsdio command line interface

    Options:
      --version                    Show the version and exit.
      -v, --verbose                Increase verbosity.
      -q, --quiet                  Decrease verbosity.
      --help                       Show this message and exit.

    Commands:
      cat       Print messages to stdout as newline JSON.
      env       Information about the gpsdio environment.
      etl       Format conversion, filtering, and sorting.
      info      Print metadata about a datasource as JSON.
      insp      Open a dataset in an interactive inspector.
      load      Load newline JSON msgs from stdin to a file.


Inputs and Outputs
------------------

For the most part ``gpsdio`` can figure out which driver and compression to use
based on the file extension, but when operating on files without extensions or
reading from stdin, these flags are available on the appropriate commands:

- ``--i-drv``: Input driver name.
- ``--i-cmp``: Input compression name.
- ``--o-drv``: Output driver name.
- ``--o-cmp``: Output compression name.

Additionally, some driver specific options are available to better configure
internal behaviors, inputs, outputs, filtering, etc.  Flags can be used multiple
times to use multiple options.  These features are exposed with the following
flags:

- ``--i-do``: Input driver option.
- ``--i-co``: Input compression option.
- ``--o-do``: Output driver option.
- ``--o-co``: Output compression option.

Help information about a given driver can be found with:

.. code-block:: console

    # For drivers
    $ gpsdio env --driver-help $NAME

    # For compression
    $ gpsdio env --compression-help $NAME

This command combines all of the above with ``gpsdio etl`` to read and write a
file without an extension while setting input/output driver/compression options:

.. code-block:: console

    $ gpsdio etl \
        INFILE \
        OUTFILE \
        --i-drv NewlineJSON \
        --i-cmp GZIP \
        --o-drv MsgPack \
        --o-cmp BZ2 \
        --i-do name=val \
        --i-co name=val \
        --o-do name=val \
        --o-co name=val


cat
---

Added in ``0.0.2``.

Similar to unix ``cat``, this command prints the messages contained within a
file as newline delimited JSON.

.. code-block:: console

    $ gpsdio cat sample-data/types.msg.gz                                                                                                             ⏎
    {"status": "Moored", "maneuver": 0, "repeat": 0, "turn": 0, "type": 1, "mmsi": 354490000, "device": "stdin", "lon": -76.3487, "raim": false, "class": "AIS", "scaled": true, "course": 217.0, "second": 58, "radio": 266634, "lat": 36.873, "speed": 0.0, "heading": 345, "accuracy": false}
    {"status": "Under way using engine", "maneuver": 0, "repeat": 0, "turn": 0, "type": 2, "mmsi": 366989394, "device": "stdin", "lon": -90.4067, "raim": false, "class": "AIS", "scaled": true, "course": 230.5, "second": 8, "radio": 4486, "lat": 29.9855, "speed": 0.0, "heading": 51, "accuracy": true}
    ...


env
---

Added in ``0.0.2``.

Information about the ``gpsdio`` environment like a list of registered drivers,

.. code-block:: console

    $ gpsdio env --drivers                                                                                                                            ⏎
    NewlineJSON - ('r', 'w', 'a')
    MsgPack - ('r', 'w', 'a')

a list of registered compression drivers,

.. code-block:: console

    $ gpsdio env --compression
    GZIP - ('r', 'w', 'a')
    BZ2 - ('r', 'w', 'a')

and help information for drivers.

.. code-block:: console

    $ gpsdio env --driver-help NewlineJSON

    Access data stored as newline delimited JSON.  Driver options are passed to
    ``newlinejson.open()``.

    https://github.com/geowurster/newlinejson

    $ gpsdio env --compression-help GZIP

    Access data stored as GZIP using Python's builtin ``gzip`` library.  Driver
    options are passed to ``gzip.open()``, unless the input path is a file-like
    object, in which case they are passed to ``gzip.GzipFile()``.

    https://docs.python.org/3/library/gzip.html


etl
---

Added in ``0.0.2``.

General purpose command for **E**\xtracting, **T**\ransforming, and **L**\oading
data.  Can also filter and sort data.  Sorting requires loading the entire file
into memory.  Filter expressions are handled by Python's ``eval()`` that only has
access to a limited scope.

.. code-block:: console

    $ gpsdio etl \
        sample-data/types.json \
        filtered.msg.gz \
        --filter "type == 3" \
        --o-drv NewlineJSON \
        --sort mmsi


info
----

Added in ``0.0.5``.

Print information about the data contained within a file as serialized JSON.
To print output to a single line use ``--indent None``.  Additional information
is also available, but can create a very cluttered output so it is off by default.

.. code-block::

    $ gpsdio info sample-data/types.msg
    {
        "bounds": [
            -123.0387,
            19.3668,
            -76.3487,
            49.1487
        ],
        "count": 20,
        "max_timestamp": "2010-05-02T00:00:00.000000Z",
        "min_timestamp": "2010-04-28T00:09:56.000000Z",
        "num_unique_field": 94,
        "num_unique_mmsi": 20,
        "num_unique_type": 20,
        "sorted": false
    }


insp
----

Added in ``0.0.2``.

Open a datasource and start a Python interpreter.  Very handy for seeing what
is in a given file.  Additional interpreters are supported.  This:

.. code-block:: console

    $ gpsdio insp sample-data/types.json --ipython
    gpsdio 0.0.6 Interactive Inspector Session (Python 2.7.10)
    Try "help(src)" or "next(src)".
    In [1]: print(next(src))


is anologous to doing:

.. code-block:: console

    $ ipython
    Python 2.7.10 (default, Jun 10 2015, 19:42:47)
    Type "copyright", "credits" or "license" for more information.

    IPython 3.2.1 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    In [1]: import gpsdio

    In [2]: with gpsdio.open('sample-data/types.json') as src:
       ...:     print(next(src))


load
----

Added in ``0.0.2``.

Read newline delimited JSON messages from ``stdin`` and write to a file.

.. code-block:: console

    $ cat sample-data/types.json | gpsdio load OUT.json
