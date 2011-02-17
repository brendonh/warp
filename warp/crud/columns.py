"""
Storm column subtypes that map to Warp's CRUD proxies.
"""

import pytz
from datetime import datetime

from storm.locals import *

def utcnow():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)

class UTCDateTime(DateTime):
    def __init__(self):
        super(UTCDateTime, self).__init__(
            tzinfo=pytz.UTC, 
            default_factory = utcnow)


class NonEmptyUnicode(Unicode):
    """
    A Unicode column that cannot be empty
    """


class Text(Unicode):
    """
    Render edit boxes as a text area instead of a one-line input
    """
    pass


class HTML(Unicode):
    """
    Render edit boxes as a big HTML text area instead of a one-line input
    """
    pass



class Image(RawStr):
    """
    Do magic file upload stuff, and display result in an <img> tag
    """
    pass


class Price(Int):
    """
    Price in dollars, stored as an integer (cents).
    """
