from zope.interface import implements

from twisted.web.resource import IResource

from warp.common.avatar import Avatar
from warp.runtime import store



class LoginBase(object):

    isLeaf = True

    def render(self, request):
        self.doIt(request)
        url = "/%s" % "/".join(request.postpath)
        request.redirect(url)
        return "Redirecting..."



class LoginHandler(LoginBase):
    implements(IResource)

    def doIt(self, request):
        if request.method != 'POST':
            return

        [email] = request.args.get('email', [None])
        [password] = request.args.get('password', [None])

        if not (email and password):
            return

        avatar = store.find(Avatar,
                            Avatar.email == email.decode("utf-8"),
                            Avatar.password == password.decode("utf-8")
                            ).one()

        if avatar is not None:
            request.session.setAvatar(avatar)



class LogoutHandler(LoginBase):

    def doIt(self, request):
        request.session.setAvatar(None)

