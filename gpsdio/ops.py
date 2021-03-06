"""
Operations
"""


import six


def sort(stream, field, default=None):

    """
    A generator to sort data by the specified field.  Requires the entire stream
    to be held in memory.  Messages lacking the specified field are dropped.

    Parameters
    ----------
    stream : iter
        Iterator producing one message per iteration.
    field : str, optional
        Field to sort by.
    """

    for msg in sorted(stream, key=lambda x: x.get(field, default)):
        yield msg


def filter(expressions, stream):

    """
    A generator to filter a stream of data with boolean Pythonic expressions.
    Multiple expressions can be provided but only messages that evaluate as
    `True` for all will be yielded.

    `eval()` is used for expression evaluation but it is given a modified global
    scope that doesn't include some blacklisted items like `exec()`, `eval()`, etc.

    Example:

        >>> import gpsdio
        >>> criteria = ("type in (1, 2, 3)", "lat' in msg", "mmsi == 366268061")
        >>> with gpsdio.open('sample-data/types.msg.gz') as stream:
        ...     for msg in gpsdio.ops.filter(stream, criteria):
        ...        # Do something

    Parameter
    ---------
    stream : iter
        An iterable producing one message per iteration.
    expressions : str or tuple
        A single expression or multiple expressions to be applied to each
        message.  Only messages that pass all filters will be yielded

    Yields
    ------
    dict
        Messages that pass all expressions.
    """

    if isinstance(expressions, six.string_types):
        expressions = expressions,

    scope_blacklist = ('eval', 'compile', 'exec', 'execfile', 'builtin', 'builtins',
                       '__builtin__', '__builtins__', 'globals', 'locals')

    global_scope = {
        k: v for k, v in globals().items() if k not in ('builtins', '__builtins__')}
    global_scope['__builtins__'] = {
        k: v for k, v in globals()['__builtins__'].items() if k not in scope_blacklist}
    global_scope['builtins'] = global_scope['__builtins__']

    for msg in stream:
        local_scope = msg.copy()
        local_scope['msg'] = msg
        for expr in expressions:
            try:
                result = eval(expr, global_scope, local_scope)
            except NameError:
                # A message doesn't contain something in the expression so just
                # force a failure since we don't need to check the other expressions.
                result = False

            if not result:
                break
        else:
            yield msg


def msg2geojson(msg):

    """
    **Experimental**

    Convert a single positional message to GeoJSON.  `lat` and `lon` are used
    to create the geometry and all other fields are placed in the `properties`
    key.

    Input:

        {
          "radio": 0,
          "course": 321.1000061035,
          "accuracy": 0,
          "maneuver": 0,
          "lon": 94.9923782349,
          "mmsi": 373061000,
          "repeat": 0,
          "turn": 0,
          "raim": false,
          "type": 1,
          "status": 0,
          "speed": 9.6999998093,
          "second": 59,
          "lat": -12.2402667999,
          "spare": 0,
          "heading": 320,
          "timestamp": "2015-01-01T00:00:00.000000Z"
        }

    Output:

        {
            "type": "Feature",
            "properties": {
                "radio": 0,
                "course": 321.1000061035,
                "accuracy": 0,
                "maneuver": 0,
                "mmsi": 373061000,
                "repeat": 0,
                "turn": 0,
                "raim": false,
                "type": 1,
                "status": 0,
                "speed": 9.6999998093,
                "second": 59,
                "spare": 0,
                "heading": 320,
                "timestamp": "2015-01-01T00:00:00.000000Z"
            },
            "geometry": {
                "type": "Point",
                "coordinates": (94.9923782349, -12.2402667999)
        }

    Parameters
    ----------
    msg : dict
        GPSd message.

    Returns
    -------
    dict
        GeoJSON
    """

    y = msg.pop('lat')
    x = msg.pop('lon')

    return {
        'type': 'Feature',
        'properties': {
            k: v for k, v in six.iteritems(msg) if (k != 'lat' or k != 'lon')},
        'geometry': {
            'type': 'Point',
            'coordinates': (x, y)
        }
    }


def geojson(stream):

    """
    **Experimental**

    Converts a stream of messages to GeoJSON features with point geometries.
    Non-positional messages are dropped.

    Currently, message type is ignored and only the lat/lon fields are used
    to determine if a message is positional.  Ultimately output messages
    will have the same schema but some internal validation work must first
    be completed.

    Parameters
    ----------
    stream : iter
        GPSd messages.

    Yields
    ------
    dict
        GeoJSON features.
    """

    for msg in stream:
        try:
            yield msg2geojson(msg)
        # Non-posit message
        except KeyError:
            pass
