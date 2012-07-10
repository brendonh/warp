from storm.locals import *

from twisted.web.server import Session, Site, Request

from warp.common.avatar import Avatar
from warp.runtime import config, avatar_store
from warp.common.avatar import SessionManager #DBSession


class WarpRequest(Request):
    def finish(self):
        rv = Request.finish(self)

        avatar_store.rollback()
        avatar_store.commit()

        # Some requests, like those for static files, don't have store
        store = getattr(self, 'store', None)
        if store:
            # Roll back and then commit, so that no transaction
            # is left open between requests.
            if store is not avatar_store:
                store.rollback()
                store.commit()

            # Some use cases involve setting store.request in
            # getRequestStore, so remove request.store here to
            # avoid a circular reference GC.
            del self.store

        return rv


class WarpSite(Site):

    requestFactory = WarpRequest
    sessionManager = SessionManager()

    def makeSession(self):
        return self.sessionManager.createSession()

    def getSession(self, uid):
        session = self.sessionManager.getSession(uid)

        if session is None:
            raise KeyError(uid)

        if session.isPersistent:
            return session

        if session.hasAvatar():
            maxAge = config.get("sessionMaxAge")
            if maxAge is not None and session.age() > maxAge:
                session.addFlashMessage("You were logged out due to inactivity", _domain="_warp:login")
                session.setAvatarID(None)

        return session

