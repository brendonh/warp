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

        subCommand = options.subCommand
        if subCommand:
            cmd = {
                'skeleton': doSkeleton,
                'node': doNode,
                'crud': doCrud,
                'adduser': doAddUser,
                'console': doConsole,
                'command': doCommand,
            }[subCommand]

            if cmd not in _skipConfig:
                loadConfig(options)
            cmd(options)
            raise SystemExit

        configModule = loadConfig(options)
        config = runtime.config
        port = config['port']
        factory = config['warpSite']

        if config.get('ssl'):
            from warp.webserver import sslcontext
            service = internet.SSLServer(port, factory,
                                         sslcontext.ServerContextFactory())
        else:
            service = internet.TCPServer(port, factory)

        if hasattr(configModule, 'mungeService'):
            service = configModule.mungeService(service)

        doStartup(options)
        return service

_skipConfig = []

def skipConfig(fn):
    _skipConfig.append(fn)
    return fn

def getSiteDir(options):
    """Utility function to get the `siteDir` out of `options`"""
    return FilePath(options['siteDir'])


def doStartup(options):
    """Utility function to execute the startup function"""
    configModule = reflect.namedModule(options['config'])
    if hasattr(configModule, 'startup'):
        configModule.startup()


def loadConfig(options):
    """Load the Warp config"""
    siteDir = FilePath(options['siteDir'])
    sys.path.insert(0, siteDir.path)

    configModule = reflect.namedModule(options['config'])
    config = configModule.config
    runtime.config.update(config)
    runtime.config['siteDir'] = siteDir
    runtime.config['warpDir'] = FilePath(runtime.__file__).parent()
    store.setupStore()
    translate.loadMessages()

    factory = site.WarpSite(resource.WarpResourceWrapper())
    runtime.config['warpSite'] = factory

    return configModule


def needConfig(f):
    """Decorator to call `loadConfig` when needed"""
    def wrapper(options):
        loadConfig(options)
        f(options)
    return wrapper

@skipConfig
def doSkeleton(options):
    """Execute the `skeleton` sub-command"""
    from warp.tools import skeleton
    print 'Creating skeleton...'
    skeleton.createSkeleton(getSiteDir(options))


def doNode(options):
    """Execute the `node` sub-command"""
    from warp.tools import skeleton
    nodes = getSiteDir(options).child('nodes')
    if not nodes.exists():
        print 'Please run this from a Warp site directory'
        return
    skeleton.createNode(nodes, options.subOptions['name'])


def doCrud(options):
    """Execute the `crud` sub-command"""
    from warp.tools import autocrud
    nodes = getSiteDir(options).child('nodes')
    if not nodes.exists():
        print 'Please run this from a Warp site directory'
        return
    subOptions = options.subOptions
    autocrud.autocrud(nodes, subOptions['name'], subOptions['model'])


def doAddUser(options):
    """Execute the `adduser` sub-command"""
    from warp.tools import adduser
    adduser.addUser()


def doConsole(options):
    """Execute the `console` sub-command"""
    import code
    doStartup(options)
    locals = {'store': runtime.store}
    c = code.InteractiveConsole(locals)
    c.interact()


def doCommand(options):
    """Execute the `command` sub-command"""
    obj = reflect.namedObject(options.subOptions['fqn'])
    doStartup(options)
    obj()


serviceMaker = WarpServiceMaker()
