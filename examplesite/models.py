import pytz

from storm.locals import *

from warp.runtime import expose


class Person(Storm):
    __storm_table__ = "person"

    id = Int(primary=True)
    name = Unicode()
    birthdate = DateTime(tzinfo=pytz.UTC)
    note = Unicode()
    alive = Bool()

expose(Person)
