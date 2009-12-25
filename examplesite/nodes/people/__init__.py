try:
    import json
except ImportError:
    import simplejson as json

from mako.template import Template

from storm.locals import Desc

from warp.runtime import store, templateLookup, internal, exposedStormClasses
from warp import helpers
from warp.crud.model import CrudModel
from warp.crud import colproxy
from warp.helpers import link, getNode


from models import Person

model = Person

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
            self.obj.name,
            getNode("people"), 
            "view", [self.obj.id])

    def render_proxy_note(self):
        return colproxy.AreaProxy(self.obj, "note")

    def name(self):
        return self.obj.name

    crudColumns = ("name", "birthdate", "note", "alive")
    crudTitles = ("Name", "Birthdate", "My Notes", "Alive?")



def render_index(request):
    return helpers.renderLocalTemplate(request, "index.mak", 
                                       model=model.__warp_crud__)


def render_list_json(request):

    params = dict((k, request.args.get(k, [''])[0])
                  for k in ('_search', 'page', 'rows', 'sidx', 'sord'))

    # XXX Todo -- Search

    sortCol = getattr(model, params['sidx'])
    if params['sord'] == 'desc':
        sortCol = Desc(sortCol)

    rowsPerPage = int(params['rows'])
    start = (int(params['page']) - 1) * rowsPerPage
    end = start + rowsPerPage

    totalResults = store.find(model).count()
    
    results = list(store.find(model).order_by(sortCol)[start:end])

    makeRow = lambda row: [row.renderListView(colName)
                           for colName in row.listColumns]

    crudClass = model.__warp_crud__

    rows = [{'id': row.id, 
             'cell': makeRow(crudClass(row))}
            for row in results]

    (totalPages, addOne) = divmod(totalResults, rowsPerPage)
    if addOne: totalPages += 1
        
    
    obj = {
        'total': totalPages,
        'page': params['page'],
        'records': len(results),
        'rows': rows,
    }

    return json.dumps(obj)



def _getCrudTemplate():
    if 'crudTemplate' not in internal:
        internal['crudTemplate'] = Template(
            '<%inherit file="/site.mak" /><%include file="/crud/crud.mak" />',
            lookup=templateLookup,
            output_encoding="utf-8")
    return internal['crudTemplate']



def render_view(request):   
    objID = int(request.resource.args[0])
    obj = store.get(model, objID)

    return helpers.renderTemplateObj(request,
                                     _getCrudTemplate(),
                                     obj=model.__warp_crud__(obj))



def render_edit(request):
    objID = int(request.resource.args[0])
    obj = store.get(model, objID)

    return helpers.renderTemplateObj(request,
                                     _getCrudTemplate(),
                                     obj=model.__warp_crud__(obj))


def render_save(request):
    bits = json.load(request.content)

    errors = []
    actions = []

    for (key, val) in bits.iteritems():

        try:
            model, objID, attr = key.split(u'-')
            objID = int(objID)
        except ValueError:
            errors.append((key, u"Invalid key: %s" % key))
            continue

        try:
            model = exposedStormClasses[model]
        except KeyError:
            errors.append((key, u"Unknown model for key '%s'" % key))
            continue

        try:
            model.__warp_crud__
        except AttributeError:
            errors.append((key, u"Model has no crud class for key '%s'" % key))
            continue

        obj = store.get(model, objID)
        if obj is None:
            errors.append((key, u"Invalid ID for key '%s'" % key))
            continue

        try:
            attr = str(attr)
        except UnicodeEncodeError:
            errors.append((key, u"Invalid attribute name for key '%s'" % key))
            continue

        # XXX TODO -- Access check goes here (or, uh, somewhere)
        # ...

        crud = model.__warp_crud__(obj)
        actions.append( (key, crud, attr, val) )


    if errors:
        return json.dumps({
                'success': False,
                'errors': errors
                })


    for (key, crud, attr, val) in actions:
        error = crud.save(attr, val)
        if error is not None:
            errors.append((key, error))


    if errors:
        store.rollback()
        return json.dumps({
                'success': False,
                'errors': errors
                })

    store.commit()

    # XXX TODO -- Somehow figure out redirect URL here
    return json.dumps({
            "success":True
            })
