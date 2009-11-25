from zope.interface import implements

from twisted.internet import defer
from twisted.python import failure

from twisted.web import resource, guard

from twisted.cred.portal import IRealm, Portal
from twisted.cred import error, credentials
from twisted.cred.checkers import ICredentialsChecker, AllowAnonymousAccess

from warp import runtime
from warp.store.avatar import UserAvatar

def getWrapper(config):
    checkers = [AllowAnonymousAccess, WarpCredChecker()]
    return guard.HTTPAuthSessionWrapper(
        Portal(WarpRealm(), checkers),
        [guard.DigestCredentialFactory('md5', config['domain'])])



# Temporary
class GuardedResource(resource.Resource):
    def getChild(self, path, request):
        return self

    def render(self, request):
        return "Authorized! (%s)" % request.avatar



class WarpRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if resource.IResource in interfaces:
            return resource.IResource, GuardedResource(), lambda: None
        raise NotImplementedError()



class WarpCredChecker(object):
    implements(ICredentialsChecker)

    credentialInterfaces = (credentials.IUsernamePassword,
                            credentials.IUsernameHashedPassword)

    
    def requestAvatarId(self, credentials):

        store = runtime['store']
        avatar = store.find(UserAvatar, UserAvatar.email == credentials.username.decode("utf-8")).one()

        if avatar is None:
            return defer.fail(error.UnauthorizedLogin())

        return defer.maybeDeferred(credentials.checkPassword, avatar.password
                                   ).addCallback(self._cbPasswordMatch, avatar)



    def _cbPasswordMatch(self, matched, avatar):
        if matched:
            return avatar.id
        else:
            return failure.Failure(error.UnauthorizedLogin())

