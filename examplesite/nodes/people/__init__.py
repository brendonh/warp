import pytz

from storm.locals import *


class Person(Storm):    
    id = Integer(primary=True)
    name = Unicode()
    birthdate = Datetime(tzinfo=pytz.UTC)

