import textwrap

from twisted.python import reflect

from storm.properties import PropertyColumn

from warp.tools import skeleton


def autocrud(nodes, name, modelFQN):
    model = reflect.namedObject(modelFQN)

    schema = [a for a in dir(model) if isinstance(getattr(model, a), PropertyColumn)]

    if 'id' not in schema:
        print "Sorry, this code isn't clever enough to auto-crud models with no id"
        return

    listCols = ["id"]
    if 'name' in schema:
        listCols.append("name")

    crudCols = schema[:]
    crudCols.remove('id')

    if 'name' in crudCols:
        crudCols.remove('name')
        crudCols.insert(0, 'name')
        
    listColumns = ", ".join('"%s"' % c for c in listCols)
    crudColumns = textwrap.fill(", ".join('"%s"' % c for c in crudCols))

    nodeContent = crudTemplate % {
        'listColumns': listColumns,
        'crudColumns': crudColumns,
        'model': modelFQN.rsplit('.', 1)[1],
        'node': name
    }

    skeleton.createNode(nodes, name, createIndex=False, nodeContent=nodeContent)
    



crudTemplate = """
from warp.crud.model import CrudModel
from warp.crud import colproxy, render
from warp.helpers import link, getNode, renderLocalTemplate, url
from warp.runtime import expose, store

from models import %(model)s

class Crud%(model)s(CrudModel):

    listColumns = (%(listColumns)s,)

    crudColumns = (%(crudColumns)s,)

    listAttrs = {
        'id': {'width': 50, 'align': 'center'},
        'name': {'width': 200},
    }

    def render_list_name(self, request):
        return link(
            self.name(request),
            getNode("%(node)s"), 
            "view", [self.obj.id])

    def name(self, request):
        return self.obj.name

    def parentCrumb(self, request):
        return getNode("%(node)s")

expose(%(model)s, Crud%(model)s)

renderer = render.CrudRenderer(%(model)s)
"""


    
