from zope.interface import implements

from twisted.web import resource, guard
from twisted.cred.portal import IRealm, Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse


class GuardedResource(resource.Resource):
    def getChild(self, path, request):
        return self

    def render(self, request):
        return "Authorized!"


class WarpRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if resource.IResource in interfaces:
            return resource.IResource, GuardedResource(), lambda: None
        raise NotImplementedError()


def getWrapper(config):
    checkers = [InMemoryUsernamePasswordDatabaseDontUse(joe='blow')]
    return guard.HTTPAuthSessionWrapper(
        Portal(WarpRealm(), checkers),
        [guard.DigestCredentialFactory('md5', config['domain'])])
