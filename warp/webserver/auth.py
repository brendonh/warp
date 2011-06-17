from zope.interface import implements

from twisted.web.resource import IResource

from warp.common.avatar import Avatar
from warp.runtime import store, config



class LoginBase(object):

    isLeaf = True

    def render(self, request):
        self.doIt(request)
        
        if request.session.avatar is not None and request.session.afterLogin is not None:
            url = request.session.afterLogin
            request.session.afterLogin = None
        else:
            url = "/%s" % "/".join(request.postpath)

        request.redirect(url)
        return "Redirecting..."


def defaultCheckPassword(avatar, password):
    return avatar.password == password.decode("utf-8")


class LoginHandler(LoginBase):
    implements(IResource)

    def doIt(self, request):
        if request.method != 'POST':
            return

        [email] = request.args.get('email', [None])
        [password] = request.args.get('password', [None])

        if not (email and password):
            request.session.addFlashMessage("Login failed: Email or password not given",
                                            _domain="_warp:login")
            return

        avatar = store.find(Avatar,
                            Avatar.email == email.decode("utf-8")
                            ).one()

        checker = config.get('checkPassword', defaultCheckPassword)
        
        if avatar is None or not checker(avatar, password):
            request.session.addFlashMessage("Login failed: Email or password incorrect",
                                            _domain="_warp:login")
            return

        request.session.setAvatar(avatar)


class LogoutHandler(LoginBase):

    def doIt(self, request):
        request.session.setAvatar(None)

