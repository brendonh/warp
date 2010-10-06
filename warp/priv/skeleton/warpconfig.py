from warp.common import access as a

config = {
    'domain': 'localhost',
    'port': 8080,
    'db': "sqlite:warp.sqlite",
    'trace': False,
    'default': 'home',
    "defaultRoles": ("anon",),

    "roles": {
        "anon": a.Role({}, default=(a.Allow(),))
        },

}
