try:
    import json
except ImportError:
    import simplejson as json

from mako.template import Template

from storm.locals import Desc

from warp.runtime import store, templateLookup, internal
from warp import helpers

from models import Person

model = Person

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
