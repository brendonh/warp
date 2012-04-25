import time
from datetime import datetime

from storm.locals import *
from warp import runtime
from warp.common import access


class Avatar(Storm):
    __storm_table__ = "warp_avatar"

    id = Int(primary=True)
    email = Unicode()
    password = Unicode()

    _roles = None
    def _getRoles(self):
        if self._roles is None:
            roleLookup = runtime.config['roles']
            avatar_roles = runtime.avatar_store.find(
                AvatarRole,
                AvatarRole.avatar == self
            ).order_by(AvatarRole.position)
            self._roles = tuple(
                [roleLookup[ar.role_name]
                    for ar in avatar_roles if ar.role_name in roleLookup] +
                [roleLookup[r] for r in
                    runtime.config['defaultRoles']]
            )

        return self._roles
    roles = property(_getRoles)


    _user = None
    def _getAppUser(self):
        if self._user is None:
            getUser = runtime.config.get('getAppUser')
            if getUser is None:
                raise NotImplementedError("No getAppUser callback configured")

            self._user = getUser(self)
        return self._user
    user = property(_getAppUser)


    def __repr__(self):
        return "<Avatar '%s'>" % self.email.encode("utf-8")


_MESSAGES = {}

def nowstamp():
    return int(time.mktime(datetime.utcnow().timetuple()))


class SessionManager(object):
    """
    Default DB-backed session handling
    """

    def createSession(self):
        uid = self._mkuid()
        session = DBSession()
        session.uid = uid
        runtime.avatar_store.add(session)
        runtime.avatar_store.commit()
        return session

    def getSession(self, uid):
        return runtime.avatar_store.get(DBSession, uid)


class DBSession(Storm):
    __storm_table__ = "warp_session"

    uid = RawStr(primary=True)
    avatar_id = Int()
    avatar = Reference(avatar_id, Avatar.id)
    touched = Int(default_factory=nowstamp)

    language = u"en_US"
    messages = None
    afterLogin = None

    _touch_granularity = 10

    def __storm_loaded__(self):
        if self.language is None:
            self.language = u"en_US"
        if self.touched is None:
            self.touched = nowstamp()
            runtime.avatar_store.commit()

    def addFlashMessage(self, msg, *args, **kwargs):
        if self.uid not in _MESSAGES:
            _MESSAGES[self.uid] = []
        _MESSAGES[self.uid].append((msg, args, kwargs))

    def getFlashMessages(self, clear=True):
        if self.uid not in _MESSAGES:
            return []
        messages = _MESSAGES[self.uid][:]
        if clear:
            del _MESSAGES[self.uid]
        return messages


    def hasAvatar(self):
        return self.avatar_id is not None

    def setAvatarID(self, avatarID):
        self.avatar_id = avatarID
        runtime.avatar_store.commit()

    def age(self):
        return nowstamp() - self.touched

    def touch(self):
        if self.age() > self._touch_granularity:
            self.touched = nowstamp()
            runtime.avatar_store.commit()

    def __repr__(self):
        return "<Session '%s'>" % self.uid


# ---------------------------


class AvatarRole(Storm):
    __storm_table__ = "warp_avatar_role"

    id = Int(primary=True)

    avatar_id = Int()
    avatar = Reference(avatar_id, "Avatar.id")

    role_name = RawStr()

    position = Int()
