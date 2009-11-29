config = {
    'domain': 'localhost',
    'port': 9999,
    'db': "postgres://brendonh:arthur@localhost:5432/warptest",
    'default': 'people',
}


def startup():
    import setupdb
    setupdb.setup()
