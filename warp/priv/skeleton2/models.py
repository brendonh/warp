import pytz
from datetime import datetime

from storm.locals import *

from warp.crud import columns

class Widget(Storm):
    __storm_table__ = 'widgets'

    id = Int(primary=True)

    name = columns.NonEmptyUnicode(default=u"")
    description = columns.Text(default=u"")
    
    is_available = Bool(default=False)
    image = columns.Image()
    
    created = DateTime(tzinfo=pytz.UTC, default_factory = lambda: pytz.UTC.localize(datetime(1970, 1, 1)))
