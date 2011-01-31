from OpenSSL import SSL

from warp.runtime import config

class ServerContextFactory:

    def getContext(self):
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_certificate_file(config['ssl']['certificate'])
        ctx.use_privatekey_file(config['ssl']['private'])
        return ctx
