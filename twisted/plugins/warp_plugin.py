from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.web.server import Site

from warp.webserver import guard
from warp.store import store


class Options(usage.Options):
    optParameters = []


class WarpServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "warp"
    description = "Warp webserver"
    options = Options

    def makeService(self, options):

        # XXX Todo: optionally get it from options later
        config = __import__('config').config

        store.setupStore(config)
        wrapper = guard.getWrapper(config)
        factory = Site(wrapper)
        return internet.TCPServer(config["port"], factory)


serviceMaker = WarpServiceMaker()
