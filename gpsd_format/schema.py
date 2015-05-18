"""
Schema definitions and functions to transform rows
"""


import six

from ._schema_def import DATETIME_FORMAT
from ._schema_def import datetime2str
from ._schema_def import fields_by_msg_type
from ._schema_def import str2datetime
from ._schema_def import VERSIONS


CURRENT = VERSIONS[max(VERSIONS.keys())]
default = {
    field: CURRENT[field]['default'] for field in CURRENT.keys() if 'default' in CURRENT[field]
}

schema_import_functions = {
    field: CURRENT[field]['import'] for field in CURRENT if CURRENT[field].get('import', None) is not None
}
schema_export_functions = {
    field: CURRENT[field]['export'] for field in CURRENT if CURRENT[field].get('export', None) is not None
}
schema_types = {
    field: CURRENT[field]['type'] for field in CURRENT if CURRENT[field].get('type', None) is not None
}
schema_cast_functions = schema_types.copy()
schema_cast_functions.update(schema_import_functions)


def validate_msg(row, ignore_missing=False, skip_failures=False, schema=CURRENT):

    """
    Validate that a row contains all fields required by its type and that they
    are of the required types. Returns True if valid, False if fields are
    missing or of wrong type.
    """

    res = True

    def add_invalid(key, value):
        if skip_failures:
            if '__invalid__' not in row:
                row['__invalid__'] = {}
            row['__invalid__'][key] = value

    try:
        for key, value in row.items():
            if key == '__invalid__':
                continue
            try:
                if key not in schema:
                    continue
                fieldschema = schema[key]
                if value is None:
                    if not fieldschema.get('null', False):
                        add_invalid(key, ("null", row.pop(key)))
                        res = False
                else:
                    vt = type(value)
                    origt = t = fieldschema.get('type', str)

                    # Hack to allow both UTF-encoded str and unicode
                    # strings - this seems to be container dependent,
                    # and actually converting using import/export
                    # would be to expensive and this is generally not
                    # that usefull
                    if t is str or t is unicode:
                        t = six.string_types

                    # Hack to allow ints where floats should be used,
                    # as the container format might convert whole
                    # numbers into ints under our feet.
                    if t is float and vt in six.integer_types:
                        vt = float

                    if not issubclass(vt, t):
                        if isinstance(origt, (list, tuple)):
                            name = [item.__name__ for item in origt]
                        else:
                            name = origt.__name__
                        add_invalid(key, (name, row.pop(key)))
                        res = False
                    elif 'test' in fieldschema and not fieldschema['test'](value):
                        add_invalid(key, ('test failed', row.pop(key)))
                        res = False
            except Exception as e:
                add_invalid(key, (str(e), row.pop(key)))
                res = False

        if not ignore_missing:
            if 'type' not in row:
                add_invalid('__missing_keys__', ('type',))
                res = False
            else:
                default_keys = set(get_default_msg(int(row['type']), schema=schema, optional=False).keys())
                row_keys = set(row.keys())
                if len(default_keys - row_keys) != 0:
                    add_invalid('__missing_keys__', tuple(default_keys - row_keys))
                    res = False

    except Exception as e:
        add_invalid('__exception__', str(e))
        res = False

    return res

def complete_msg(msg, schema=CURRENT):
    """Add any fields that are not present with their default values"""

    res = get_default_msg(int(msg['type']), schema=schema)
    res.update(msg)

    return res


def strip_msg(msg, schema=CURRENT):
    """Remove any fields that do not belong"""

    res = {'type': msg['type']}
    msg_type = int(msg['type'])

    for key, value in msg.iteritems():
        if key in fields_by_msg_type[msg_type]:
            res[key] = value

    return res


def force_msg(msg, schema=CURRENT, keep_fields=False):

    """
    Make sure a msg has only valid fields by removing unrecognized fields and
    adding missing ones. Input msg must have a `type` field containing the
    message type.

    No field validation or type-casting is performed EXCEPT the `type`
    field is always forced to be an `int` in order to avoid unnecessarily
    raising an exception when a string value is encountered.  If the string
    cannot be cast to an `int` then an exception will be raised.

    Parameters
    ----------
    msg : dict
        Input msg - must contain a `type` key
    keep_fields : bool
        Keep extraneous fields
    schema : dict
        The schema definition to use

    Returns
    -------
    dict
        Input msg forced to a specific message type
    """

    if not keep_fields:
        msg = strip_msg(msg, schema=schema)
    return complete_msg(msg, schema=schema)

    message = get_default_msg(int(msg['type']), schema=schema)


def import_msg(row, skip_failures=False, cast_values=False):

    """
    Cast all values in a row from their import types as defined by the
    schema definition

    Parameters
    ----------
    row : dict
        Input row with normalized field names
    skip_failures: bool
        If False, reading a row with an attribute value that does not match
        the schema type for that attribute will cause an exception.
    cast_values: bool
        If true, an attempt will be made to cast values to the right types
        even for primitive types where the import type and the python type is the same.

    Returns
    -------
    dict
    """

    if cast_values:
        import_functions = schema_cast_functions
    else:
        import_functions = schema_import_functions

    # This function sometimes receives rows that are not exclusively AIS message types
    # The assumption is that the user wants them to be there since there are enough ways
    # to explicitly strip them off
    output = {}
    for field, val in six.iteritems(row):
        if field in import_functions:
            try:
                output[field] = import_functions[field](val)
            except Exception as e:
                if not skip_failures:
                    raise Exception("%s=%s: %s: %s" % (field, repr(val), type(e), e))
                if '__invalid__' not in output:
                    output['__invalid__'] = {}
                output['__invalid__'][field] = val
        else:
            output[field] = val

    return output


def export_msg(row, skip_failures=False):

    """
    Cast all values in a row to their export types as defined by the
    schema definition

    Parameters
    ----------
    row : dict
        Input row adhering to the GPSD schema
    skip_failures: bool
        If False, reading a row with an attribute value that does not match
        the schema type for that attribute will cause an exception.
    """

    # This function sometimes receives rows that are not exclusively AIS message types
    # The assumption is that the user wants them to be there since there are enough ways
    # to explicitly strip them off
    output = {}
    for field, val in row.items():
        if field in schema_export_functions:
            try:
                output[field] = schema_export_functions[field](val)
            except Exception as e:
                if not skip_failures:
                    raise Exception("%s: %s: %s" % (field, type(e), e))
                if '__invalid__' not in output:
                    output['__invalid__'] = {}
                output['__invalid__'][field] = str(val)
        else:
            output[field] = val

    return output


def get_default_msg(msg_type, schema=CURRENT, optional=True):

    """
    Get an AIS message containing nothing but default values

    Parameters
    ----------
    msg_type : int
        Message type ID
    schema : dict, optional
        Schema definition from which to extract default values
    """

    try:
        res = {field: schema[field]['default']
               for field in fields_by_msg_type[msg_type]
               if 'default' in schema[field] and (optional or schema[field].get('required', True))}
        res['type'] = msg_type
        return res
    except Exception as e:
        raise ValueError("Invalid AIS message type: %s: %s" % (msg_type, e))
