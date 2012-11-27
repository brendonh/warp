import tempfile
import os.path

try:
    import json
except ImportError:
    import simplejson as json

from twisted.web.resource import NoResource
from twisted.web import static

from storm.locals import Desc, Reference

from warp.runtime import (templateLookup, internal,
                          exposedStormClasses, config)
from warp import helpers
from warp.crud import form


class CrudRenderer(object):

    def __init__(self, model, crudModel=None):
        self.model = model
        self.crudModel = crudModel or helpers.getCrudClass(model)
        self.tinyTemplate = None

    def getTinyTemplate(self):
        if not self.tinyTemplate:
            self.tinyTemplate = """
<html>
  <head>
    <link rel="stylesheet" href="%s/_warp/reset.css" type="text/css"></link>
  </head>
  <body>
    %%s
  </body>
</html>
""" % config.get("baseURL", '')
        return self.tinyTemplate

    def renderTemplate(self, request, templatePath):
        objID = int(request.resource.args[0])
        obj = request.store.get(self.model, objID)

        return helpers.renderTemplateObj(request,
                                         self._getViewTemplate(),
                                         crud=self.crudModel(obj),
                                         subTemplate=templatePath)


    def renderLocalTemplate(self, request, filename):

        # Get a path to the local template relative to
        # something in Mako's templateLookup dirs.
        localNode = helpers.getCrudNode(self.crudModel).__file__
        relPath = os.path.relpath(
            os.path.dirname(localNode),
            os.path.abspath("templates"))
        templatePath = "/%s/%s" % (relPath, filename)

        return self.renderTemplate(request, templatePath)


    def render_index(self, request):
        return helpers.renderTemplateObj(request,
                                         self._getListTemplate(),
                                         model=self.crudModel,
                                         allowCreate=self.crudModel.allowCreate,
                                         subTemplate="list.mak")


    def render_list_json(self, request):

        params = dict((k, request.args.get(k, [''])[0])
                      for k in ('_search', 'page', 'rows', 'sidx', 'sord'))

        # XXX Todo -- Search

        sortCol = getattr(self.model, params['sidx'])

        if isinstance(sortCol, Reference):
            sortCol = sortCol._local_key[0]

        if params['sord'] == 'desc':
            sortCol = Desc(sortCol)

        rowsPerPage = int(params['rows'])
        start = (int(params['page']) - 1) * rowsPerPage
        end = start + rowsPerPage

        conditions = self.crudModel.listConditions(self.model, request)

        totalResults = request.store.find(self.model, *conditions).count()

        results = list(request.store.find(self.model, *conditions).order_by(sortCol)[start:end])

        exclude = json.loads(request.args.get('exclude', ['[]'])[0])

        makeRow = lambda row: [row.renderListView(colName, request)
                               for colName in row.listColumns
                               if colName not in exclude]

        rows = [{'id': '.'.join(str(getattr(row, k)) for k in row.__storm_primary__)
                       if hasattr(row, '__storm_primary__')
                       else row.id,
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


    def _getListTemplate(self):
        if 'crudListTemplate' not in internal:
            internal['crudListTemplate'] = templateLookup.get_template('/crud/wrapper.mak')
        return internal['crudListTemplate']


    def _getViewTemplate(self):
        if 'crudTemplate' not in internal:
            internal['crudTemplate'] = templateLookup.get_template('/crud/wrapper.mak')
        return internal['crudTemplate']

    _getEditTemplate = _getViewTemplate


    def getRequestObject(self, request):
        try:
            objID = int(request.resource.args[0])
        except Exception:
            return None
        return request.store.get(self.model, objID)

    def render_view(self, request):
        obj = self.getRequestObject(request)
        if obj is None:
            template = templateLookup.get_template("/error_404.mak")
            return helpers.renderTemplateObj(request, template)

        return helpers.renderTemplateObj(request,
                                         self._getViewTemplate(),
                                         crud=self.crudModel(obj),
                                         subTemplate="form.mak")



    def render_edit(self, request):
        obj = self.getRequestObject(request)
        if obj is None:
            template = templateLookup.get_template("/error_404.mak")
            return helpers.renderTemplateObj(request, template)

        crud = self.crudModel(obj)

        return helpers.renderTemplateObj(request,
                                         self._getEditTemplate(),
                                         crud=crud,
                                         redirect=crud.saveRedirect(request),
                                         subTemplate="form.mak")


    def render_save(self, request):
        objects = json.load(request.content)
        (success, info) = form.applyForm(objects, request)

        if not success:
            request.store.rollback()
            return json.dumps({
                    'success': False,
                    'errors': info
                    })


        try:
            request.store.commit()
        except Exception, e:
            request.store.rollback()
            return json.dumps({
                    'success': False,
                    'errors': [(None, "Database error: %s" % e.message)]})


        results = dict((k, [o.id for o in v])
                       for (k,v) in info.iteritems())

        return json.dumps({
                "success": True,
                "results": results,
                })


    def render_create(self, request, template=None):

        presets = json.loads(request.args.get('presets', [''])[0] or '{}')
        noEdit = json.loads(request.args.get('noedit', [''])[0] or '[]')
        fakeID = request.args.get('fakeID', [''])[0] or 1

        if template is None:
            template = templateLookup.get_template("/crud/form.mak")

        fakeObj = self.model()

        fakeObj.fakeID = 'n%s' % fakeID
        fakeObj.noEdit = noEdit

        for (k,v) in presets.iteritems():
            setattr(fakeObj, k, v)

        defaulter = getattr(fakeObj, "__warp_setdefaults__", None)
        if defaulter is not None:
            defaulter()

        return helpers.renderTemplateObj(request, template,
                                         crud=self.crudModel(fakeObj))


    def render_delete(self, request):
        objID = int(request.resource.args[0])
        obj = request.store.get(self.model, objID)

        if obj is not None:
            request.store.remove(obj)
            request.store.commit()

        request.redirect(helpers.url(request.node))
        return "Redirecting..."


    def render_image(self, request):
        try:
            className, objID, attrName = request.resource.args
            objID = int(objID)
            klass = exposedStormClasses[className][0]
            obj = request.store.get(klass, objID)
        except Exception, e:
            import traceback
            traceback.print_exc()
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
        return self.getTinyTemplate() % form


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

        return self.getTinyTemplate() % """
<em style="line-height: 1.5em; color: #090; font-weight: normal;">[Uploaded OK]</em>
<script type="text/javascript">
  parent.jQuery.fn.warpform.submissionCallbacks[%s](%s, "%s");
</script>""" % (submitID, callbackID, tfName)
