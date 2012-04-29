from zope.interface import implements

import sys

from twisted.python import usage, reflect
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.web.server import Site
from twisted.python.filepath import FilePath

from warp.webserver import resource, site
from warp.common import store, translate
from warp.iwarp import IWarpService
from warp import runtime


class SkeletonOptions(usage.Options):
    optParameters = (
        ("siteDir", "d", ".", "Base directory of the warp site"),
    )

class NodeOptions(usage.Options):
    def parseArgs(self, name):
        self['name'] = name

class CrudOptions(usage.Options):
    def parseArgs(self, name, model):
        self['name'] = name
        self['model'] = model


class CommandOptions(usage.Options):
    def parseArgs(self, fqn):
        self['fqn'] = fqn

class Options(usage.Options):
    optParameters = (
        ("siteDir", "d", ".", "Base directory of the warp site"),
    )

    subCommands = (
        ("skeleton", None, SkeletonOptions, "Copy Warp site skeleton into current directory"),
        ("node", None, NodeOptions, "Create a new node"),
        ("crud", None, CrudOptions, "Create a new CRUD node"),
        ("adduser", None, usage.Options, "Add a user (interactive)"),
        ("console", None, usage.Options, "Python console with Warp runtime available"),
        ("command", "c", CommandOptions, "Run a site-specific command"),
    )


class WarpServiceMaker(object):
    implements(IServiceMaker, IPlugin, IWarpService)
    tapname = "warp"
    description = "Warp webserver"
    options = Options

    def makeService(self, options):

        siteDir = FilePath(options['siteDir'])

        sys.path.insert(0, siteDir.path)

        if options.subCommand == "skeleton":
            print "Creating skeleton..."
            from warp.tools import skeleton
            skeleton.createSkeleton(siteDir)
            raise SystemExit

        configModule = __import__('warpconfig')
        config = configModule.config
        runtime.config.update(config)
        runtime.config['siteDir'] = siteDir
        runtime.config['warpDir'] = FilePath(runtime.__file__).parent()
        store.setupStore()
        translate.loadMessages()

        if options.subCommand == "node":
            nodes = siteDir.child("nodes")
            if not nodes.exists():
                print "Please run this from a Warp site directory"
                raise SystemExit

            from warp.tools import skeleton
            skeleton.createNode(nodes, options.subOptions['name'])
            raise SystemExit

        elif options.subCommand == 'crud':
            nodes = siteDir.child("nodes")
            if not nodes.exists():
                print "Please run this from a Warp site directory"
                raise SystemExit

            from warp.tools import autocrud
            autocrud.autocrud(nodes, options.subOptions['name'], options.subOptions['model'])
            raise SystemExit

        elif options.subCommand == 'adduser':
            from warp.tools import adduser
            adduser.addUser()
            raise SystemExit


        factory = site.WarpSite(resource.WarpResourceWrapper())
        runtime.config['warpSite'] = factory

        if hasattr(configModule, 'startup'):
            configModule.startup()

        if options.subCommand == "console":
            import code
            locals = {'store': runtime.store}
            c = code.InteractiveConsole(locals)
            c.interact()
            raise SystemExit
        
        if options.subCommand == 'command':
            raise SystemExit
            

        if config.get('ssl'):
            from warp.webserver import sslcontext
            service = internet.SSLServer(config['port'], factory,
                                         sslcontext.ServerContextFactory())
        else:
            service = internet.TCPServer(config["port"], factory)

        if hasattr(configModule, 'mungeService'):
            service = configModule.mungeService(service)

        return service


serviceMaker = WarpServiceMaker()
