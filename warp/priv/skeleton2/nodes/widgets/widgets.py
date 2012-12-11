
from warp.crud.model import CrudModel
from warp.crud import colproxy, render
from warp.helpers import link, getNode, renderLocalTemplate, url
from warp.runtime import expose

from models import Widget

def linkAsParent(request):
        return link("Widgets", getNode("widgets"), "index")

class CrudWidget(CrudModel):

    listColumns = ("id", "name",)

    crudColumns = ("name", "created", "description", "image", "is_available",)

    listAttrs = {
        'id': {'width': 50, 'align': 'center'},
        'name': {'width': 200},
    }

    def render_list_name(self, request):
        return link(
            self.name(request),
            getNode("widgets"), 
            "view", [self.obj.id])

    def name(self, request):
        return self.obj.name

    def parentCrumb(self, request):
        return getNode("widgets")

expose(Widget, CrudWidget)

renderer = render.CrudRenderer(Widget)
