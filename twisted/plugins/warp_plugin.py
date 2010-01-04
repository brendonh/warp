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
from warp.iwarp import IWarpService
from warp import runtime


class SkeletonOptions(usage.Options):
    optParameters = (
        ("siteDir", "d", ".", "Base directory of the warp site"),
    )


class Options(usage.Options):
    optParameters = (
        ("siteDir", "d", ".", "Base directory of the warp site"),
    )

    subCommands = (
        ("skeleton", None, SkeletonOptions, "Copy Warp site skeleton into current directory"),
    )


class WarpServiceMaker(object):
    implements(IServiceMaker, IPlugin, IWarpService)
    tapname = "warp"
    description = "Warp webserver"
    options = Options

    def makeService(self, options):

        siteDir = FilePath(options['siteDir'])

        if options.subCommand == "skeleton":
            print "Creating skeleton..."
            from warp.tools import skeleton
            skeleton.createSkeleton(siteDir)
            raise SystemExit


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
