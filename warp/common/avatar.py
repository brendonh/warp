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
            self._roles = tuple(
                runtime.config['roles'][ar.role_name]
                for ar in runtime.store.find(
                    AvatarRole, AvatarRole.avatar == self
                    ).order_by(AvatarRole.position)
                ) + (runtime.config['roles']["anon"],)

        return self._roles
    roles = property(_getRoles)   
    
    def __repr__(self):
        return "<Avatar '%s'>" % self.email.encode("utf-8")


class DBSession(Storm):
    __storm_table__ = "warp_session"

    uid = RawStr(primary=True)
    avatar_id = Int()
    avatar = Reference(avatar_id, Avatar.id)

    def setAvatar(self, avatar):
        self.avatar = avatar
        runtime.store.commit()

    def touch(self):
        # Warp sessions don't expire (yet),
        # so they don't do anything when poked
        pass

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
