"""
Objects used to define
"""


import datetime
from operator import lt, gt, ge, le
import six
from gpsdio.errors import SchemaError


__all__ = (
    'DATETIME_FORMAT', 'build_validator', 'str2datetime', 'datetime2str',
    'BaseValidator', 'All', 'Any', 'DateTime', 'Float', 'FloatRange', 'In',
    'Instance', 'IntIn', 'Int', 'IntRange', 'Range'
)


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def build_validator(schema):
    out = {}
    for mtype, fields in six.iteritems(schema):
        out[mtype] = {k: v['validate'] for k, v in six.iteritems(fields)}
    return out


def str2datetime(string):

    """
    Convert a string to a datetime.

    Parameters
    ----------
    string : str or datetime.datetime
        Matching the global `DATETIME_FORMAT`.

    Returns
    -------
    datetime.datetime
    """

    if isinstance(string, datetime.datetime):
        return string

    return datetime.datetime(
        year=int(string[:4]),
        month=int(string[5:7]),
        day=int(string[8:10]),
        hour=int(string[11:13]),
        minute=int(string[14:16]),
        second=int(string[17:19]),
        microsecond=int(string[20:-1])
    )


def datetime2str(datetime_obj):

    """
    Convert a datetime object to a string.

    Parameters
    ----------
    datetime_obj : datetime.datetime or str
    """

    # This is expensive to validate so just assume the user got it right
    if isinstance(datetime_obj, six.string_types):
        return datetime_obj

    return datetime_obj.strftime(DATETIME_FORMAT)


class BaseValidator(object):

    """
    - An allowed type
    - A function to validate a value
    - A function to coerce from string
    - A function to serialize (as string, int, float, etc.)
    """

    types = object

    @staticmethod
    def coerce(obj):
        return obj

    @staticmethod
    def serialize(obj):
        return obj

    def validate(self, obj):

        """
        Let `check_type()` be the default validation.
        """

        return obj

    def check_type(self, obj):
        if isinstance(obj, self.types):
            return obj
        else:
            raise SchemaError("Value '{}' is of type '{}', not one of: '{}'".format(
                obj, type(obj), self.types))

    def __call__(self, obj):
        return self.validate(self.check_type(obj))

    def __repr__(self):
        return "{name}()".format(name=self.__class__.__name__)


class Range(BaseValidator):

    def __init__(self, minimum=None, maximum=None, include_min=True, include_max=True):
        if minimum is None and maximum is None:
            raise ValueError("Need a value for minimum or maximum.")
        self.minimum = minimum
        self.maximum = maximum
        self.include_min = include_min
        self.include_max = include_max
        self.lt = lt
        self.le = le
        self.gt = gt
        self.ge = ge

        if self.maximum is None:
            self.lt = self.le = lambda a, b: True
        if self.minimum is None:
            self.gt = self.ge = lambda a, b: True

        if include_min and include_max:
            self.compare = self.include_both
        elif not include_min and not include_max:
            self.compare = self.exclude_both
        elif self.include_min and not self.include_max:
            self.compare = self.include_min_exclude_max
        elif not self.include_min and self.include_max:
            self.compare = self.exclude_min_include_max
        else:
            raise ValueError("Couldn't build range comparison.")

    def include_both(self, minimum, value, maximum):
        return self.ge(value, minimum) and self.le(value, maximum)

    def exclude_both(self, minimum, value, maximum):
        return self.gt(value, minimum) and self.lt(value, maximum)

    def include_min_exclude_max(self, minimum, value, maximum):
        return self.ge(value, minimum) and self.lt(value, maximum)

    def exclude_min_include_max(self, minimum, value, maximum):
        return self.gt(value, minimum) and self.le(value, maximum)

    def validate(self, obj):
        if self.compare(self.minimum, obj, self.maximum):
            return obj
        else:
            raise SchemaError("Value '{}' failed validation: {}".format(obj, repr(self)))

    def __repr__(self):
        return "{name}(minimum={min}, maximum={max}, include_min={imin}, include_max={imax})" \
            .format(name=self.__class__.__name__, min=self.minimum, max=self.maximum,
                    imin=self.include_min, imax=self.include_max)


class IntRange(Range):

    types = six.integer_types
    coerce = int


class FloatRange(Range):

    types = float
    coerce = float


class DateTime(BaseValidator):

    types = tuple([datetime.datetime] + list(six.string_types))
    coerce = str2datetime
    serialize = datetime2str

    def validate(self, obj):
        try:
            return str2datetime(obj)
        except Exception as e:
            raise SchemaError(str(e))


class IntIn(BaseValidator):

    coerce = int
    types = six.integer_types

    def __init__(self, values):
        self.values = values

    def validate(self, obj):
        if obj in self.values:
            return obj
        else:
            raise SchemaError("Value '{}' not in: {}".format(obj, self.values))

    def __repr__(self):
        return "{name}({values})".format(name=self.__class__.__name__, values=', '.join(
            str(v) for v in self.values))


class Int(BaseValidator):

    coerce = int
    types = six.integer_types


class Float(BaseValidator):

    coerce = float
    types = float


class Instance(BaseValidator):

    def __init__(self, *types):
        self.types = tuple(types)

    def __repr__(self):
        return "{name}({types})".format(
            name=self.__class__.__name__, types=', '.join([o.__name__ for o in self.types]))


class Any(BaseValidator):

    def __init__(self, *tests):
        self.tests = tests

    def validate(self, obj):
        for t in self.tests:
            try:
                return t(obj)
            except Exception:
                pass
        else:
            raise SchemaError(
                "Value '{}' failed all tests: {}".format(obj, repr(self)))

    def __repr__(self):
        return "{name}({tests})".format(
            name=self.__class__.__name__, tests=', '.join([repr(t) for t in self.tests]))


class All(BaseValidator):

    def __init__(self, *tests):
        self.tests = tests

    def validate(self, obj):
        for t in self.tests:
            try:
                obj = t(obj)
            except Exception as e:
                raise SchemaError("Value '{}' failed test '{}': {}".format(obj, t, str(e)))
        return obj

    def __repr__(self):
        return "{name}({tests})".format(
            name=self.__class__.__name__, tests=', '.join([repr(t) for t in self.tests]))


class In(BaseValidator):

    def __init__(self, values):
        self.values = values

    def validate(self, obj):
        if obj in self.values:
            return obj
        else:
            raise SchemaError("Value '{}' not in: {}".format(obj, repr(self)))

    def __repr__(self):
        return "{name}({values})".format(
            name=self.__class__.__name__, values=', '.join([str(v) for v in self.values]))
