from zope.interface import implements

from twisted.web.resource import IResource

from warp.webserver import auth, node
from warp.runtime import config

class WarpResourceWrapper(object):
    implements(IResource)

    isLeaf = False

    def __init__(self):
        node.findNodes()


    def getChildWithDefault(self, firstSegment, request):
        session = request.getSession()
        if session is not None:
            request.avatar = session.avatar

        if firstSegment == '__login__':
            return auth.LoginHandler()
        elif firstSegment == '__logout__':
            return auth.LogoutHandler()

        return WarpResource()


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


