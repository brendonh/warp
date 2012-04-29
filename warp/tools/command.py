from twisted.python import usage, reflect


class Options(usage.Options):
    """
    Run a Python function in the Warp environment
    """

    def parseArgs(self, fqn):
        self['fqn'] = fqn


def command():
    obj = reflect.namedObject(options.subOptions['fqn'])
    obj()
