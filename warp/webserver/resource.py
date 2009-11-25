from zope.interface import implements

from storm.locals import *

from twisted.web.resource import IResource
from twisted.web.server import Session, Site

from warp.store.avatar import Avatar
from warp import runtime



class WarpSite(Site):

    def makeSession(self):
        uid = self._mkuid()
        session = DBSession()
        session.uid = uid
        store = runtime['store']
        store.add(session)
        store.commit()
        return session

    def getSession(self, uid):
        store = runtime['store']
        session = store.get(DBSession, uid)

        if session is None:
            raise KeyError(uid)

        return session



class DBSession(Storm):
    __storm_table__ = "warp_session"

    uid = RawStr(primary=True)
    avatar_id = Int()
    avatar = Reference(avatar_id, Avatar.id)
        
    def setAvatar(self, avatar):
        self.avatar = avatar
        runtime['store'].commit()

    def touch(self):
        # Warp sessions don't expire (yet),
        # so they don't do anything when poked
        pass

    def __repr__(self):
        return "<Session '%s'>" % self.uid



class WarpResourceWrapper(object):
    implements(IResource)

    isLeaf = False

    def getChildWithDefault(self, firstSegment, request):
        session = request.getSession()
        if session is not None:
            request.avatar = session.avatar

        if firstSegment == '__login__':
            return LoginHandler()
        elif firstSegment == '__logout__':
            return LogoutHandler()

        return WarpResource()



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

        avatar = runtime['store'].find(Avatar,
                                       Avatar.email == unicode(email),
                                       Avatar.password == unicode(password)
                                       ).one()

        if avatar is not None:
            request.session.setAvatar(avatar)



class LogoutHandler(LoginBase):

    def doIt(self, request):
        request.session.setAvatar(None)



class WarpResource(object):
    implements(IResource)

    # You can always add a slash
    isLeaf = False

    def getChildWithDefault(self, segment, request):
        print "Segment:", segment
        return self

    def render(self, request):
        if request.avatar is None:
            loggedIn = "Not logged in."
        else:
            loggedIn = "Logged in as %s" % request.avatar.email.encode("utf-8")

        return """
%s<br />
<form method="POST" action="/__login__">
Email: <input type="text" name="email" /><br />
Pass: <input type="text" name="password" /><br />
<input type="submit" value="Log in" />
</form>
""" % loggedIn


