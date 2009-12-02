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
from warp.iwarp import IWarpService


class Options(usage.Options):
    optParameters = [
        ["siteDir", "d", ".", "Base directory of the warp site"],
        ]


class WarpServiceMaker(object):
    implements(IServiceMaker, IPlugin, IWarpService)
    tapname = "warp"
    description = "Warp webserver"
    options = Options

    def makeService(self, options):

        # XXX Todo: optionally get it from options later
        siteDir = FilePath(options['siteDir'])

        sys.path.insert(0, siteDir.path)

        configModule = __import__('warpconfig')
        config = configModule.config
        runtime.config.update(config)
        runtime.config['siteDir'] = siteDir
        store.setupStore(config)

        if hasattr(configModule, 'startup'):
            configModule.startup()

        factory = site.WarpSite(resource.WarpResourceWrapper())
        service = internet.TCPServer(config["port"], factory)

        if hasattr(configModule, 'mungeService'):
            service = configModule.mungeService(service)

        return service


serviceMaker = WarpServiceMaker()
