"""
Python 2/3 compatibility
"""


import sys


if sys.version_info[0] is 2:  # pragma no cover
    string_types = basestring,
else:  # pragma no cover
    string_types = str,
