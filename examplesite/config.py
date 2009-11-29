config = {
    'domain': 'localhost',
    'port': 9999,
    'db': "postgres://brendonh:arthur@localhost:5432/warptest",
}


def startup():
    import setupdb
    setupdb.setup()
