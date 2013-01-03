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
        ("config", "w", "warpconfig", "Config filename"),
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
            doSkeleton(options)

        configModule = reflect.namedModule(options['config'])
        config = configModule.config
        runtime.config.update(config)
        runtime.config['siteDir'] = siteDir
        runtime.config['warpDir'] = FilePath(runtime.__file__).parent()
        store.setupStore()
        translate.loadMessages()

        if options.subCommand == "node":
            doNode(options)
        elif options.subCommand == 'crud':
            doCrud(options)
        elif options.subCommand == 'adduser':
            doAddUser(options)

        factory = site.WarpSite(resource.WarpResourceWrapper())
        runtime.config['warpSite'] = factory

        if options.subCommand == "console":
            doConsole(options)
        if options.subCommand == 'command':
            doCommand(options)

        if config.get('ssl'):
            from warp.webserver import sslcontext
            service = internet.SSLServer(config['port'], factory,
                                         sslcontext.ServerContextFactory())
        else:
            service = internet.TCPServer(config["port"], factory)

        if hasattr(configModule, 'mungeService'):
            service = configModule.mungeService(service)

        return service


def getSiteDir(options):
    """Utility function to get the `siteDir` out of `options`"""
    return FilePath(options['siteDir'])


def doStartup(options):
    """Utility function to execute the startup function"""
    configModule = reflect.namedModule(options['config'])
    if hasattr(configModule, 'startup'):
        configModule.startup()


def doSkeleton(options):
    """Execute the `skeleton` sub-command"""
    print 'Creating skeleton...'
    from warp.tools import skeleton
    skeleton.createSkeleton(getSiteDir(options))
    raise SystemExit


def doNode(options):
    """Execute the `node` sub-command"""
    nodes = getSiteDir(options).child('nodes')
    if not nodes.exists():
        print 'Please run this from a Warp site directory'
        raise SystemExit

    from warp.tools import skeleton
    skeleton.createNode(nodes, options.subOptions['name'])
    raise SystemExit


def doCrud(options):
    """Execute the `crud` sub-command"""
    nodes = getSiteDir(options).child('nodes')
    if not nodes.exists():
        print 'Please run this from a Warp site directory'
        raise SystemExit

    from warp.tools import autocrud
    autocrud.autocrud(nodes, options.subOptions['name'], options.subOptions['model'])
    raise SystemExit


def doAddUser(options):
    """Execute the `adduser` sub-command"""
    from warp.tools import adduser
    adduser.addUser()
    raise SystemExit


def doConsole(options):
    """Execute the `console` sub-command"""
    import code
    doStartup(options)
    locals = {'store': runtime.store}
    c = code.InteractiveConsole(locals)
    c.interact()
    raise SystemExit


def doCommand(options):
    """Execute the `command` sub-command"""
    obj = reflect.namedObject(options.subOptions['fqn'])
    doStartup(options)
    obj()
    raise SystemExit


serviceMaker = WarpServiceMaker()
