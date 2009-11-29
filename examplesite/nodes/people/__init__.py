import pytz

from storm.locals import *


class Person(Storm):    
    id = Int(primary=True)
    name = Unicode()
    birthdate = DateTime(tzinfo=pytz.UTC)

