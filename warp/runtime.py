"""
Globally-accessible stuff (like the store) initialised at runtime, not import-time
"""

from storm.locals import Store

from mako.lookup import TemplateLookup

# Thanks to _habnabit for this clever trick!
store = Store.__new__(Store)

templateLookup = TemplateLookup.__new__(TemplateLookup)

config = {}

sql = {}

internal = {}
