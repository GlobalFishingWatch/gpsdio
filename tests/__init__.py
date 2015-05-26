"""Unittests for `gpsdio`."""


from . import *

# TODO: Move this to a util file.
def compare_msg(msg1, msg2, float_tolerance=0.00001):

    for k1, k2 in zip(sorted(list(msg1)), sorted(list(msg2))):
        v1 = msg1[k1]
        v2 = msg2[k2]
        if isinstance(v1, float) and isinstance(v2, float):
            if abs(v1 - v2) > float_tolerance:
                return False
        else:
            if v1 != v2:
                return False

    return True
