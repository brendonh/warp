from warp.common import access as a
from warp.helpers import getNode

config = {
    'domain': 'localhost',
    'port': 8080,
    'db': "sqlite:warp.sqlite",
    'trace': False,
    'default': 'home',
    "defaultRoles": ("anon",),

    "roles": {
        "anon": a.Role({
               getNode("home"): (a.Allow(),), 
            }),
        "admin": a.Role({}, default=(a.Allow(),)),
    },
}
