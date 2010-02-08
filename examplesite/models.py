import pytz

from storm.locals import *

class Person(Storm):
    __storm_table__ = "person"

    id = Int(primary=True)
    name = Unicode()
    birthdate = DateTime(tzinfo=pytz.UTC)
    note = Unicode()
    rating = Int()
    alive = Bool()


