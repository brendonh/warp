import sys

from inspect import getargspec

from twisted.python import usage, reflect
from twisted.python.filepath import FilePath

from warp.webserver import resource, site
from warp.common import store, translate
from warp import runtime


class Options(usage.Options):
    optParameters = (
        ("siteDir", "d", ".", "Base directory of the warp site"),
        ("config", "w", "warpconfig", "Config filename"),
    )

    subCommands = []


_commands = {}

# NTA XXX: This is not usable by app, because when command-line
# options are parsed app-specific information is not available yet.
# A hacky workaround would be some code in twisted.warp_plugin to
# import a "magic" app-defined module
def register(shortName=None, skipConfig=False, needStartup=False, optionsParser=None):
    """Decorator to register functions as commands. Functions must
    accept options map as the first parameter.

    Usage:

    @register(*params)
    def foo(options, arg1):
        pass
    """
    def decorator(fn):
        name = fn.__name__
        doc = fn.__doc__ or ""

        if optionsParser is None:
            class CmdOptions(usage.Options):
                def parseArgs(self, *args):
                    spec = getargspec(fn)
                    if spec.defaults:
                        raise usage.UsageError("Custom command cannot have arguments with default values")
                    if spec.varargs:
                        raise usage.UsageError("Custom command cannot take variable number of arguments")
                    if spec.keywords:
                        raise usage.UsageError("Custom command cannot take keyword arguments")

                    cmd_args = spec.args[1:]
                    count = len(cmd_args)
                    if len(args) != count:
                        raise usage.UsageError(
                            "Wrong number of arguments, %d expected:\n    twistd warp %s %s"
                            % (count, name, " ".join(["<%s>" % arg for arg in cmd_args])))
                    self["args"] = args
            klass = CmdOptions
        else:
            klass = optionsParser

        Options.subCommands.append((name, shortName, klass, doc))

        def wrapped(options):
            if not skipConfig:
                loadConfig(options)
            if needStartup:
                doStartup(options)
            fn(options, *options.subOptions.get("args", ()))

        _commands[name] = wrapped
        return wrapped
    return decorator


def maybeRun(options):
    subCommand = options.subCommand

    if subCommand:
        command = _commands[subCommand]
        command(options)
        raise SystemExit


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


# Pre-defined commands -----------------------------------------------


class SkeletonOptions(Options):
    optParameters = (
        ("siteDir", "d", ".", "Base directory of the warp site to generate"),
    )
@register(skipConfig = True, optionsParser = SkeletonOptions)
def skeleton(options):
    "Copy Warp site skeleton into current directory"
    from warp.tools import skeleton
    print 'Creating skeleton...'
    siteDir = getSiteDir(options.subOptions) or getSiteDir(options)
    skeleton.createSkeleton(siteDir)


@register()
def node(options, name):
    "Create a new node"
    from warp.tools import skeleton
    nodes = getSiteDir(options).child('nodes')
    if not nodes.exists():
        print 'Please run this from a Warp site directory'
        return
    skeleton.createNode(nodes, name)


@register()
def crud(options, name, model):
    "Create a new CRUD node"
    from warp.tools import autocrud
    nodes = getSiteDir(options).child('nodes')
    if not nodes.exists():
        print 'Please run this from a Warp site directory'
        return
    autocrud.autocrud(nodes, name, model)


@register()
def adduser(options):
    "Add a user (interactive)"
    from warp.tools import adduser
    adduser.addUser()


@register(needStartup = True)
def console(options):
    "Python console with Warp runtime available"
    import code
    locals = {'store': runtime.store}
    c = code.InteractiveConsole(locals)
    c.interact()


@register(needStartup = True, shortName = "c")
def command(options, function):
    "Run a site-specific command"
    obj = reflect.namedObject(function)
    obj()
