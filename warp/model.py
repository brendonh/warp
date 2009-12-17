from storm.locals import *


class MetaCrudModel(type):
    def __init__(klass, name, bases, dct):
        if 'model' in dct:
            dct['model'].__warp_crud__ = klass



class CrudModel(object):

    __metaclass__ = MetaCrudModel

    viewRenderers = {
        Int: lambda v: str(v),
        Unicode: lambda v: v.encode("utf-8"),
        DateTime: lambda v: v.strftime("%x %H:%M"),
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


    def defaultView(self, colName):
        val = getattr(self.obj, colName)
        valType = self.colMap[colName]
        return self.viewRenderers[valType](val)


    def renderView(self, colName):
        funcName = "render_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)()
        return self.defaultView(colName)


    def renderListView(self, colName):
        funcName = "render_list_%s" % colName
        if hasattr(self, funcName):
            return getattr(self, funcName)()
        return self.defaultView(colName)
