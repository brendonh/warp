from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

#from myproject import MyFactory


class Options(usage.Options):
    optParameters = [["port", "p", 1235, "The port number to listen on."]]


class WarpServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "warp"
    description = "Run this! It'll make your dog happy."
    options = Options

    def makeService(self, options):
        """
        Construct a TCPServer from a factory defined in myproject.
        """
        #return internet.TCPServer(int(options["port"]), MyFactory())


# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = WarpServiceMaker()
