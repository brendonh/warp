import pytz

from storm.locals import *

from warp.model import CrudModel
from warp.helpers import link, getNode


class Person(Storm):
    __storm_table__ = "person"

    id = Int(primary=True)
    name = Unicode()
    birthdate = DateTime(tzinfo=pytz.UTC)


class CrudPerson(CrudModel):

    model = Person

    listColumns = ("id", "name", "birthdate")

    listTitles = ("ID", "Name", "Birthdate")

    listAttrs = {
        'id': {'width': 50, 'align': 'center'},
        'name': {'width': 200},
        'birthdate': {'width': 150, 'align': 'center'}
    }

    def render_list_name(self):
        return link(
            self.defaultView("name"),
            getNode("people"), 
            "view", [self.obj.id])

    def name(self):
        return self.obj.name

    crudColumns = ("name", "birthdate")
    crudTitles = ("Name", "Birthdate")
