"""
Unittsts for gpsdio.schema
"""


from gpsdio import schema


def test_build_schema():
    assert sorted(schema.build_schema().keys())[:3] == [1, 2, 3]
