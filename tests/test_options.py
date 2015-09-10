"""
Unittests for gpsdio.cli.options
"""


import click
import pytest

from gpsdio.cli import options


def test_cb_indent_none():
    assert options._cb_indent(None, None, 'NONE') is None


def test_cb_indent_int():
    assert options._cb_indent(None, None, '1') is 1


def test_cb_indent_exception():
    with pytest.raises(click.BadParameter):
        options._cb_indent(None, None, 'words')
