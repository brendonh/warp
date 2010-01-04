from twisted.python import log

from storm.locals import *

from warp import runtime

def setupStore(config):

    #import storm.database
    #storm.database.DEBUG = True

    store = runtime.store
    store.__init__(create_database(config['db']))

    sqlBundle = getCreationSQL(store)
    tableExists = runtime.sql['tableExists'] = sqlBundle['tableExists']

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
            'tableExists': lambda s, t: bool(s.execute("SELECT count(*) FROM pg_class where relname = ?", (t,)).get_one()[0]),
            'creations': [
                ('warp_avatar', """
                CREATE TABLE warp_avatar (
                    id SERIAL NOT NULL PRIMARY KEY, 
                    email VARCHAR, 
                    password VARCHAR,
                    UNIQUE(email))"""),
                ('warp_session', """
                CREATE TABLE warp_session (
                    uid BYTEA NOT NULL PRIMARY KEY,
                    avatar_id INTEGER REFERENCES warp_avatar(id))"""),
                ],
            },
        'SQLiteConnection': {
            'tableExists': lambda s, t: bool(s.execute("SELECT count(*) FROM sqlite_master where name = '%s'" % t).get_one()[0]),
            'creations': [
                ('warp_avatar', """
                CREATE TABLE warp_avatar (
                    id INTEGER NOT NULL PRIMARY KEY, 
                    email VARCHAR, 
                    password VARCHAR,
                    UNIQUE(email))"""),
                ('warp_session', """
                CREATE TABLE warp_session (
                    uid BYTEA NOT NULL PRIMARY KEY,
                    avatar_id INTEGER REFERENCES warp_avatar(id))"""),
                ],
            },
    }[connType]


