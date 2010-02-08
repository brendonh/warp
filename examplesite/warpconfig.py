from nodes.people import people

from warp.common.access import Role, Allow

config = {
    'domain': 'localhost',
    'port': 9999,
    'db': "postgres://brendonh:arthur@localhost:5432/warptest",
    'default': 'people',

    'roles': {
        "admin": Role({
            "default": [Allow()]
        }),
        "anon": Role({
            people: [Allow()]
        })
     },

    'defaultRoles': ["anon"],

}


def startup():
    import setupdb
    setupdb.setup()
