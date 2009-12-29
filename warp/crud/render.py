import tempfile

try:
    import json
except ImportError:
    import simplejson as json

from twisted.web.resource import NoResource
from twisted.web import static

from mako.template import Template

from storm.locals import Desc

from warp.runtime import store, templateLookup, internal, exposedStormClasses
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
        
        makeRow = lambda row: [row.renderListView(colName, request)
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
        objects = json.load(request.content)

        (success, info) = form.applyForm(objects, request)
    
        if not success:
            store.rollback()
            return json.dumps({
                    'success': False,
                    'errors': info
                    })

        else:
            store.commit()

            results = dict((k, [o.id for o in v])
                           for (k,v) in info.iteritems())

            return json.dumps({
                    "success": True,
                    "results": results,
                    })


    def render_create(self, request):
        template = templateLookup.get_template("/crud/form.mak")

        fakeObj = self.model()

        # XXX TODO - Take a counter argument from the request here, 
        # so Javascript can product lots of these which don't conflict.
        fakeObj.fakeID = '*1'

        return helpers.renderTemplateObj(request, template, 
                                         obj=self.crudModel(fakeObj))


    def render_delete(self, request):
        objID = int(request.resource.args[0])
        obj = store.get(self.model, objID)

        if obj is not None:
            store.remove(obj)
            store.commit()

        request.redirect(helpers.url(request.node))
        return "Redirecting..."


    def render_image(self, request):
        try:
            className, objID, attrName = request.resource.args
            objID = int(objID)
            klass = exposedStormClasses[className]
            obj = store.get(klass, objID)
        except:
            return NoResource().render(request)
        
        val = getattr(obj, attrName)
        
        if val is None:
            return NoResource().render(request)
        else:
            return static.Data(val, "image/jpeg").render(request)



    def render_uploadframe(self, request):
        form = """
    <form method="post" enctype="multipart/form-data" action="%s">
      <input type="file" name="uploaded-file" />
      <input type="hidden" name="submitID" value="" />
      <input type="hidden" name="callbackID" value="" />
    </form>""" % helpers.url(request.node, "uploadfile")
        return tinyTemplate % form


    def render_uploadfile(self, request):
        content = request.args.get('uploaded-file', [''])[0]
        if not content:
            return self.render_uploadframe(request)

        tf = tempfile.NamedTemporaryFile()
        tf.write(content)
        tfName = tf.name.rsplit('/', 1)[-1]

        internal['uploadCache'][tfName] = tf

        submitID = request.args['submitID'][0]
        callbackID = request.args['callbackID'][0]

        return tinyTemplate % """
<em style="line-height: 1.5em; color: #090; font-weight: normal;">[Uploaded OK]</em>
<script type="text/javascript">
  parent.jQuery.fn.warpform.submissionCallbacks[%s](%s, "%s");
</script>""" % (submitID, callbackID, tfName)


tinyTemplate = """
<html>
  <head>
    <link rel="stylesheet" href="/_warp/reset.css" type="text/css"></link>
  </head>
  <body>
    %s
  </body>
</html>
"""
