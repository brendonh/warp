from storm.locals import *

from twisted.web.server import Session, Site

from warp.common.avatar import Avatar
from warp.runtime import store

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
        store.commit()

    def touch(self):
        # Warp sessions don't expire (yet),
        # so they don't do anything when poked
        pass

    def __repr__(self):
        return "<Session '%s'>" % self.uid
