from storm.locals import *

def setupStore(config):
    import warp
    warp.store = Store(create_database(config['db_url']))


