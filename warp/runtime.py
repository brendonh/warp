"""
Globally-accessible stuff (like the store) initialised at runtime, not import-time
"""

from storm.locals import Store

# Thanks to _habnabit for this clever trick!
store = Store.__new__(Store)

__all__ = ['store']
