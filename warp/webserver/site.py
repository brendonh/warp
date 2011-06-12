from storm.locals import *

from twisted.web.server import Session, Site, Request

from warp.common.avatar import Avatar
from warp.runtime import store, config
from warp.common.avatar import DBSession


class WarpRequest(Request):
    def processingFailed(self, reason):
        rv = Request.processingFailed(self, reason)
        store.rollback()
        store.commit()
        return rv

    def finish(self):
        rv = Request.finish(self)
        store.rollback()
        store.commit()
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

        maxAge = config.get("sessionMaxAge")
        if maxAge is not None and session.age() > maxAge:
            store.remove(session)
            store.commit()
            raise KeyError(uid)

        return session

