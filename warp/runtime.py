"""
Globally-accessible stuff (like the store) initialised at runtime, not import-time
"""

from storm.locals import Store

from mako.lookup import TemplateLookup

# Thanks to _habnabit for this clever trick!
avatar_store = Store.__new__(Store)

# Default for app code only.
# Warp never uses this name, so it can be safely changed or removed.
store = avatar_store

templateLookup = TemplateLookup.__new__(TemplateLookup)

config = {}

sql = {}

internal = {
    'uploadCache': {}
}

exposedStormClasses = {}

messages = {}

def expose(modelClass, crudClass):
    exposedStormClasses[unicode(modelClass.__name__)] = (modelClass, crudClass)
    
    # The problem with this is that in theory more than one model might use
    # the same crud class, but if that actually happens, trivially subclassing
    # the crud class will fix it.
    crudClass.__warp_model__ = modelClass

