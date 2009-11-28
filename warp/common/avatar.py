from storm.locals import *

class Avatar(Storm):
    __storm_table__ = "warp_avatar"

    id = Int(primary=True)
    email = Unicode()
    password = Unicode()

    def __repr__(self):
        return "<Avatar '%s'>" % self.email.encode("utf-8")
