import code

from twisted.python import usage
from warp.runtime import store


class Options(usage.Options):
    """
    Drop into a Python shell in the Warp environment
    """
    pass


def run():
    import readline
    locals = {'store': runtime.store}
    c = code.InteractiveConsole(locals)
    c.interact()
    raise SystemExit
