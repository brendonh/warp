"""
Storm column subtypes that map to Warp's CRUD proxies.
"""

from storm.locals import *


class NonEmptyUnicode(Unicode):
    """
    A Unicode column that cannot be empty
    """


class Text(Unicode):
    """
    Render edit boxes as a text area instead of a one-line input
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
    pass
