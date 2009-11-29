from zope.interface import implements

import sys

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.web.server import Site
from twisted.python.filepath import FilePath

from warp.webserver import resource, site
from warp.common import store
from warp import runtime


class Options(usage.Options):
    optParameters = []


class WarpServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "warp"
    description = "Warp webserver"
    options = Options

    def makeService(self, options):

        # XXX Todo: optionally get it from options later
        siteDir = FilePath('.')

        sys.path.insert(0, siteDir.path)

        configModule = __import__('config')
        config = configModule.config
        runtime.config.update(config)
        runtime.config['siteDir'] = siteDir
        store.setupStore(config)

        if hasattr(configModule, 'startup'):
            configModule.startup()

        factory = site.WarpSite(resource.WarpResourceWrapper())
        return internet.TCPServer(config["port"], factory)


serviceMaker = WarpServiceMaker()
