
"""
Driz
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A fast lightweight k-v storage for hobbyists.

:copyright: (c) 2025-present Sougata Jana
:license: MIT, see LICENSE for more details.

"""

__title__ = "driz"
__license__ = "MIT"
__copyright__ = "Copyright 2025-present Sougata Jana"
__author__ = "Sougata Jana"
__version__ = "0.0.1"


from .client import DB
from .converter import date, datetime, time, timedelta
from .errors import *
from .schema import Column, Schema
from .query import *