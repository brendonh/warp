from zope.interface import implements

from storm.locals import *

from twisted.web.resource import IResource
from twisted.web.server import Session, Site

from warp.store.avatar import Avatar
from warp import runtime


class WarpResourceWrapper(object):
    implements(IResource)

    isLeaf = False

    def getChildWithDefault(self, firstSegment, request):
        request.getSession()
        if firstSegment == '__login__':
            return self.login(request)
        elif firstSegment == '__logout__':
            return self.logout(request)
        return WarpResource()

    
    def login(self, request):
        print "LOGIN"
        return WarpResource()
        #if request.method != 'POST':
        #    raise Exception("Oh noes!")
        

    def logout(self, request):
        print "LOGOUT"
        return WarpResource()



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
        
    def touch(self):
        # Warp sessions don't expire (yet),
        # so they don't do anything when poked
        pass

    def __repr__(self):
        return "<Session '%s'>" % self.uid



class WarpResource(object):
    implements(IResource)

    # You can always add a slash
    isLeaf = False

    def getChildWithDefault(self, segment, request):
        print "Segment:", segment
        return self

    def render(self, request):
        return "Hello World"


