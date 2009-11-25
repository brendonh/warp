from twisted.python import log

from storm.locals import *

import warp

def setupStore(config):
    store = warp.runtime['store'] = Store(create_database(config['db']))

    sqlBundle = getCreationSQL(store)
    tableExists = sqlBundle['tableExists']

    for (table, creationSQL) in sqlBundle['creations']:

        if not tableExists(store, table):

            # Unlike log.message, this works during startup
            print "~~~ Creating Warp table '%s'" % table

            store.execute(creationSQL)
            store.commit()



def getCreationSQL(store):
    connType = store._connection.__class__.__name__
    return {
        'PostgresConnection': {
            'tableExists': lambda s, t: bool(s.execute("SELECT count(*) FROM pg_class where relname = '%s'" % t).get_one()[0]),
            'creations': [
                ('warp_avatar', """
                CREATE TABLE warp_avatar (
                    id SERIAL NOT NULL PRIMARY KEY, 
                    email VARCHAR, 
                    password VARCHAR,
                    UNIQUE(email))"""),
                ],
            },
    }[connType]
