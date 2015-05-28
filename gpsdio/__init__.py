# encoding:utf-8


"""Tools for working with the GPSD format in JSON or msgpack."""


from .core import open
from .core import filter
from .core import sort
from . import schema
from . import validate


__version__ = '0.0.2'
__author__ = 'Kevin Wurster, Egil Moeller'
__email__ = 'kevin@skytruth.org, egil@skytruth.org, '
__source__ = 'https://github.com/SkyTruth/gpsdio'
__license__ = """
Copyright 2014-2015 SkyTruth
Authors:
Kevin Wurster <kevin@skytruth.org>
Egil Möller <egil@skytruth-org>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
