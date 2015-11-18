"""
Cythonified field validators.
"""


import sys

from cpython cimport array

from gpsdio.errors import SchemaError


cdef int MININT = -1000000000
cdef int MAXINT = 1000000000
cdef float MAXFLOAT = sys.float_info.max
cdef float MINFLOAT = sys.float_info.min


cdef class Int:

    def coerce(self, obj):
        return int(obj)

    def __call__(self, int obj):
        return obj
    
    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


cdef class Float:

    def coerce(self, obj):
        return float(obj)

    cdef float validate(self, float obj):
        return obj

    def __call__(self, obj):
        try:
            return self.validate(obj)
        except Exception:
            raise SchemaError("Object `{}' of type {} is not a float".format(obj, type(obj)))
        
    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


cdef bint _int_include_both(int minimum, int value, int maximum):
    return minimum <= value <=maximum

cdef bint _int_exclude_both(int minimum, int value, int maximum):
    return minimum < value < maximum

cdef bint _int_include_min_exclude_max(int minimum, int value, int maximum):
    return minimum <= value < maximum

cdef bint _int_exclude_min_include_max(int minimum, int value, int maximum):
    return minimum < value <= maximum

cdef bint _float_include_both(float minimum, float value, float maximum):
    return minimum <= value <=maximum

cdef bint _float_exclude_both(float minimum, float value, float maximum):
    return minimum < value < maximum

cdef bint _float_include_min_exclude_max(float minimum, float value, float maximum):
    return minimum <= value < maximum

cdef bint _float_exclude_min_include_max(float minimum, float value, float maximum):
    return minimum < value <= maximum


cdef class IntRange:

    cdef int minimum
    cdef int maximum
    cdef bint include_min
    cdef bint include_max

    def __init__(self, int minimum=MININT, int maximum=MAXINT, bint include_min=True, bint include_max=True):
        self.minimum = minimum
        self.maximum = maximum
        self.include_min = include_min
        self.include_max = include_max


    def coerce(self, obj):
        return int(obj)

    cdef bint validate(self, int obj) except -1:
        if self.include_min and self.include_max:
            return _int_include_both(self.minimum, obj, self.maximum)
        elif self.include_min and not self.include_max:
            return _int_include_min_exclude_max(self.minimum, obj, self.maximum)
        elif not self.include_min and self.include_max:
            return _int_exclude_min_include_max(self.minimum, obj, self.maximum)
        elif not self.include_min and not self.include_max:
            return _int_exclude_both(self.minimum, obj, self.maximum)
        else:
            return -1

    def __call__(self, int obj):
        if self.validate(obj):
            return obj
        else:
            raise SchemaError("Value {} failed test: {}".format(obj, repr(self)))

    def __repr__(self):
        return "{n}(minimum={mi}, maximum={ma}, include_min={imi}, include_max={ima})".format(
            n=self.__class__.__name__, mi=self.minimum, ma=self.maximum,
            imi=self.include_min, ima=self.include_max)


cdef class FloatRange:

    cdef float minimum
    cdef float maximum
    cdef bint include_min
    cdef bint include_max

    def __init__(self, float minimum=MINFLOAT, float maximum=MAXFLOAT, bint include_min=True, bint include_max=True):
        self.minimum = minimum
        self.maximum = maximum
        self.include_min = include_min
        self.include_max = include_max

    def coerce(self, obj):
        return float(obj)

    cdef bint validate(self, float obj) except -1:
        if self.include_min and self.include_max:
            return _float_include_both(self.minimum, obj, self.maximum)
        elif self.include_min and not self.include_max:
            return _float_include_min_exclude_max(self.minimum, obj, self.maximum)
        elif not self.include_min and self.include_max:
            return _float_exclude_min_include_max(self.minimum, obj, self.maximum)
        elif not self.include_min and not self.include_max:
            return _float_exclude_both(self.minimum, obj, self.maximum)
        else:
            return -1

    def __call__(self, float obj):
        if self.validate(obj):
            return obj
        else:
            raise SchemaError("Value {} failed test: {}".format(obj, repr(self)))

    def __repr__(self):
        return "{n}(minimum={mi}, maximum={ma}, include_min={imi}, include_max={ima})".format(
            n=self.__class__.__name__, mi=self.minimum, ma=self.maximum,
            imi=self.include_min, ima=self.include_max)


cdef class IntIn:

    cdef array.array a
    cdef int a_len

    def __init__(self, values):
        self.a = array.array('I', values)
        self.a_len = len(values)

    def coerce(self, obj):
        return int(obj)

    cdef bint validate(self, int obj):
        cdef int i
        for i in range(self.a_len):
            if obj == self.a.data.as_ints[i]:
                return 1
        else:
            return 0

    def __call__(self, int obj):
        if self.validate(obj):
            return obj
        else:
            raise SchemaError("Value `{}' not in: {}".format(obj, self.a))

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, list(self.a))
