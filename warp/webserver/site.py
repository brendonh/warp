from storm.locals import *

from twisted.web.server import Session, Site, Request

from warp.common.avatar import Avatar
from warp.runtime import store
from warp.common.avatar import DBSession


class WarpRequest(Request):
    def processingFailed(self, reason):
        rv = Request.processingFailed(self, reason)
        store.rollback()
        return rv
        


class WarpSite(Site):

    requestFactory = WarpRequest

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

