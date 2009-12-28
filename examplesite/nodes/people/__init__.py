from warp.crud.model import CrudModel
from warp.crud import colproxy, render
from warp.helpers import link, getNode

from models import Person

class CrudPerson(CrudModel):

    model = Person

    listColumns = ("id", "name", "birthdate", "rating")
    crudColumns = ("name", "birthdate", "note", "rating", "alive")

    listAttrs = {
        'id': {'width': 50, 'align': 'center'},
        'name': {'width': 200},
        'birthdate': {'width': 150, 'align': 'center'},
        'rating': {'width': 50, 'align': 'center'},
    }

    def render_list_name(self, request):
        return link(
            self.obj.name,
            getNode("people"), 
            "view", [self.obj.id])

    def render_proxy_note(self, request):
        return colproxy.AreaProxy(self.obj, "note")

    def name(self, request):
        return self.obj.name


renderer = render.CrudRenderer(Person)
