from storm.locals import *

from warp.crud import colproxy

class MetaCrudModel(type):
    def __init__(klass, name, bases, dct):
        if 'model' in dct:
            dct['model'].__warp_crud__ = klass


class CrudModel(object):

    __metaclass__ = MetaCrudModel

    editRenderers = {
        Int: colproxy.StringProxy,
        Unicode: colproxy.StringProxy,
        DateTime: colproxy.DateProxy,
        Bool: colproxy.BooleanProxy,
    }

    listAttrs = {}

    listTitles = None
    crudTitles = None

    colMap = None


    def __init__(self, obj):
        self.obj = obj

        if self.colMap is None:
            self.__class__.colMap = dict(
                (v.name, k.__class__)
                for (k,v) in self.model._storm_columns.iteritems())


    def name(self):
        return self.obj.id


    def _getProxy(self, colName):
        funcName = "render_proxy_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)()
        return self.defaultProxy(colName)


    def defaultProxy(self, colName):
        val = getattr(self.obj, colName)
        valType = self.colMap[colName]
        return self.editRenderers[valType](self.obj, colName)


    def renderListView(self, colName):
        funcName = "render_list_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)()
        return self._getProxy(colName).render_view()


    def renderView(self, colName):
        funcName = "render_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)()
        return self._getProxy(colName).render_view()


    def renderEdit(self, colName):
        funcName = "render_edit_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)()
        return self._getProxy(colName).render_edit()

        
    def save(self, colName, val):
        funcName = "save_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)(val)
        return self._getProxy(colName).save(val)
