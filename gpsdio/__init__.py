# encoding:utf-8


"""
AIS I/O with Python, dictionaries, and the GPSd AIVDM schema.
"""


import logging

# Immediately set up so that other modules have access to the logger
logging.basicConfig()
logger = logging.getLogger('gpsdio')

from .core import open
from .core import filter
from .core import sort
from . import schema
from . import validate


__version__ = '0.0.7'
__author__ = 'Egil Moeller, Kevin Wurster'
__email__ = 'egil@skytruth.org, kevin@skytruth.org'
__source__ = 'https://github.com/SkyTruth/gpsdio'
__license__ = """
Copyright 2014-2015 SkyTruth
Authors:
Egil Möller <egil@skytruth-org>
Kevin Wurster <kevin@skytruth.org>

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
