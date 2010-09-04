from storm.locals import *

from warp.crud import colproxy, columns
from warp import helpers

class CrudModel(object):

    editRenderers = {
        Int: colproxy.IntProxy,
        Unicode: colproxy.StringProxy,
        DateTime: colproxy.DateTimeProxy,
        Date: colproxy.DateProxy,
        Bool: colproxy.BooleanProxy,
        Reference: colproxy.ReferenceProxy,
        ReferenceSet: colproxy.ReferenceSetProxy,
        RawStr: colproxy.RawStringProxy,
        Float: colproxy.FloatProxy,
        Enum: colproxy.StormEnumProxy,

        # Warp column subclasses
        columns.NonEmptyUnicode: colproxy.NonEmptyStringProxy,
        columns.Text: colproxy.AreaProxy,
        columns.HTML: colproxy.HTMLAreaProxy,
        columns.Image: colproxy.ImageProxy,
        columns.Price: colproxy.PriceProxy,
    }

    listAttrs = {}

    listTitles = None
    crudTitles = None

    showListLink = True

    gridAttrs = {
        'rowNum': "10",
        'rowList': "[10,20,30]",
        'sortname': "'id'",
        'sortorder': "'asc'",
        'viewrecords': "true",
    }


    def __init__(self, obj):
        self.obj = obj


    def name(self, request):
        return self.obj.id


    def parentCrumb(self, request):
        parent = self.parent(request)
        if parent is not None:
            return helpers.getCrudObj(parent)


    def parent(self, request):
        return None

    def linkAsParent(self, request):
        return helpers.link(self.name(request), 
                            helpers.getCrudNode(self), 
                            "view", 
                            [self.obj.id])


    def saveRedirect(self, request):
        return helpers.url(request.node, 'view', request.resource.args)


    def getProxy(self, colName, request):
        funcName = "render_proxy_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)(request)
        return self.defaultProxy(colName)


    def defaultProxy(self, colName):
        val = getattr(self.obj, colName)
        # Avoid triggering the property __get__
        valType = self.obj.__class__.__dict__[colName].__class__
        return self.editRenderers[valType](self.obj, colName)


    def renderListView(self, colName, request):
        funcName = "render_list_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)(request)
        return self.getProxy(colName, request).render_view(request)


    def renderView(self, colName, request):
        funcName = "render_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)(request)
        return self.getProxy(colName, request).render_view(request)


    def renderEdit(self, colName, request):
        funcName = "render_edit_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)(request)
        return self.getProxy(colName, request).render_edit(request)

        
    def save(self, colName, val, request):
        funcName = "save_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)(val, request)
        return self.getProxy(colName, request).save(val, request)

