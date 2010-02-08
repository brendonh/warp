from storm.locals import *

from twisted.web.server import Session, Site

from warp.common.avatar import Avatar
from warp.runtime import store
from warp.common.avatar import DBSession


class WarpSite(Site):

    def makeSession(self):
        uid = self._mkuid()
        session = DBSession()
        session.uid = uid
        store.add(session)
        store.commit()
        return session

    def getSession(self, uid):
        session = store.get(DBSession, uid)

        if session is None:
            raise KeyError(uid)

        return session




