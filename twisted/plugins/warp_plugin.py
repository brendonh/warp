from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from warp.iwarp import IWarpService
from warp import runtime, command

class WarpServiceMaker(object):
    implements(IServiceMaker, IPlugin, IWarpService)
    tapname = "warp"
    description = "Warp webserver"
    options = command.Options

    def makeService(self, options):

        command.maybeRun(options)

        configModule = command.loadConfig(options)
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

        command.doStartup(options)
        return service


serviceMaker = WarpServiceMaker()
