try:
    import json
except ImportError:
    import simplejson as json

from mako.template import Template

from storm.locals import Desc

from warp.runtime import store, templateLookup, internal
from warp import helpers
from warp.crud import form


class CrudRenderer(object):

    def __init__(self, model):
        self.model = model
        self.crudModel = model.__warp_crud__


    def render_index(self, request):
        template = templateLookup.get_template("/crud/list.mak")
        return helpers.renderTemplateObj(request, template, 
                                         model=self.crudModel)


    def render_list_json(self, request):

        params = dict((k, request.args.get(k, [''])[0])
                      for k in ('_search', 'page', 'rows', 'sidx', 'sord'))

        # XXX Todo -- Search

        sortCol = getattr(self.model, params['sidx'])
        if params['sord'] == 'desc':
            sortCol = Desc(sortCol)

        rowsPerPage = int(params['rows'])
        start = (int(params['page']) - 1) * rowsPerPage
        end = start + rowsPerPage

        totalResults = store.find(self.model).count()
    
        results = list(store.find(self.model).order_by(sortCol)[start:end])
        
        makeRow = lambda row: [row.renderListView(colName)
                               for colName in row.listColumns]

        rows = [{'id': row.id, 
                 'cell': makeRow(self.crudModel(row))}
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



    def _getCrudTemplate(self):
        if 'crudTemplate' not in internal:
            internal['crudTemplate'] = Template(
                '<%inherit file="/site.mak" /><%include file="/crud/crud.mak" />',
                lookup=templateLookup,
                output_encoding="utf-8")
        return internal['crudTemplate']


    def render_view(self, request):   
        objID = int(request.resource.args[0])
        obj = store.get(self.model, objID)
        
        return helpers.renderTemplateObj(request,
                                         self._getCrudTemplate(),
                                         obj=self.crudModel(obj))



    def render_edit(self, request):
        objID = int(request.resource.args[0])
        obj = store.get(self.model, objID)

        return helpers.renderTemplateObj(request,
                                         self._getCrudTemplate(),
                                         obj=self.crudModel(obj),
                                         redirect=helpers.url(request.node, 'view', request.resource.args))


    def render_save(self, request):
        bits = json.load(request.content)
        errors = form.applyForm(bits)
    
        if errors:
            store.rollback()
            return json.dumps({
                    'success': False,
                    'errors': errors
                    })

        else:
            store.commit()
            return json.dumps({
                    "success": True
                    })

