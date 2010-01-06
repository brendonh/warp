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

class NodeOptions(usage.Options):
    def parseArgs(self, name):
        self['name'] = name


class Options(usage.Options):
    optParameters = (
        ("siteDir", "d", ".", "Base directory of the warp site"),
    )

    subCommands = (
        ("skeleton", None, SkeletonOptions, "Copy Warp site skeleton into current directory"),
        ("node", None, NodeOptions, "Create a new node"),
        ("console", None, usage.Options, "Python console with Warp runtime available"),
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

        elif options.subCommand == "node":
            nodes = siteDir.child("nodes")
            if not nodes.exists():
                print "Please run this from a Warp site directory"
                raise SystemExit

            from warp.tools import skeleton
            skeleton.createNode(nodes, options.subOptions['name'])
            raise SystemExit

        sys.path.insert(0, siteDir.path)

        configModule = __import__('warpconfig')
        config = configModule.config
        runtime.config.update(config)
        runtime.config['siteDir'] = siteDir
        store.setupStore(config)

        if hasattr(configModule, 'startup'):
            configModule.startup()


        if options.subCommand == "console":
            import code
            locals = {'store': runtime.store}
            c = code.InteractiveConsole(locals)
            c.interact()
            raise SystemExit


        factory = site.WarpSite(resource.WarpResourceWrapper())
        service = internet.TCPServer(config["port"], factory)

        if hasattr(configModule, 'mungeService'):
            service = configModule.mungeService(service)

        return service


serviceMaker = WarpServiceMaker()
