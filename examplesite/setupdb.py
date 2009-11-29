from warp.runtime import sql, store


tableSpecs = [
    ("person", """
      CREATE TABLE person (
        id SERIAL NOT NULL PRIMARY KEY,
        name VARCHAR NOT NULL,
        birthdate TIMESTAMP WITHOUT TIME ZONE
)""")
]


def setup():
    for (table, creationSQL) in tableSpecs:
        if not sql['tableExists'](store, table):
            print "Creating table %s" % table
            store.execute(creationSQL)
            store.commit()
