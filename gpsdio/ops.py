"""
Message modification operations.
"""


import copy

import six

import gpsdio.schema


def strip_msgs(stream, keep_invalid=False, invalid_key='__invalid__'):

    """
    Remove unrecognized fields from a stream of messages.  Messages can be kept
    and moved to a specific key if desired.

    Parameters
    ----------
    stream : iter
        Iterable producing GPSd messages.
    keep_invalid : bool, optional
        Place unrecognized fields into a dictionary in `invalid_key`.
    invalid_key : str, optional
        Key to store unrecognized fields.
    """

    for msg in stream:

        # Copy the input message to make sure we don't modify the dicts outside
        # this scope.  Valid fields are removed from this `invalid` dict, which
        # just leaves us with the invalid keys
        invalid = copy.deepcopy(msg)

        m = {
            k: invalid.pop(k) for k in tuple(invalid.keys())
            if k in gpsdio.schema.fields_by_msg_type[msg['type']]}

        if keep_invalid and invalid:
            m[invalid_key] = invalid

        yield m


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


def sort(stream, field='timestamp'):

    """
    A generator to sort data by the specified field.  Requires the entire stream
    to be held in memory.  Messages lacking the specified field are dropped.

    Parameters
    ----------
    stream : iter
        Iterator producing one message per iteration.
    field : str, optional
        Field to sort by.  Defaults to sorting by `timestamp`.
    """

    queue = six.moves.queue.PriorityQueue()
    for msg in stream:
        if field in msg:
            queue.put((msg[field], msg))

    while not queue.empty():
        yield queue.get()[1]
