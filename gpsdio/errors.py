"""
gpsdio exceptions
"""


class GPSDIOException(Exception):

    """
    Base exception
    """


class SchemaError(GPSDIOException):

    """
    Schema validation failed.
    """
