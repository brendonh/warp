import pytz, operator
from datetime import datetime

from warp.runtime import internal, store, templateLookup
from warp.helpers import url, link, getNode, renderTemplateObj, getNodeByCrudClass


class BaseProxy(object):

    def __init__(self, obj, col):
        self.obj = obj
        self.col = col

    def fieldName(self):

        id = self.obj.fakeID if hasattr(self.obj, 'fakeID') else self.obj.id

        return "%s-%s-%s" % (
            self.obj.__class__.__name__,
            id,
            self.col)

    def render_view(self, request):
        return unicode(getattr(self.obj, self.col))

    
    def render_edit(self, request):
        return '<input type="text" name="warpform-%s" value="%s" />' % (
            self.fieldName(),
            getattr(self.obj, self.col))


    def save(self, val, request):
        try:
            setattr(self.obj, self.col, val)
        except (TypeError, ValueError):
            return u"Invalid value"
            


class StringProxy(BaseProxy):
    pass


class NonEmptyStringProxy(StringProxy):

    def save(self, val, request):
        if not val:
            return u"Cannot be empty"
        super(NonEmptyStringProxy, self).save(val, request)



class AreaProxy(StringProxy):
    
    def render_edit(self, request):
        return '<textarea name="warpform-%s" cols="30" rows="5">%s</textarea>' % (
            self.fieldName(),
            getattr(self.obj, self.col))



class BooleanProxy(BaseProxy):
    def render_edit(self, request):
        val = getattr(self.obj, self.col)
        if val:
            checkedBit = 'checked="checked" '
        else:
            checkedBit = ''

        return '<input type="checkbox" name="warpform-%s" class="warpform-bool" value="%s" %s/>' % (
            self.fieldName(), val, checkedBit)



class IntProxy(BaseProxy):

    def render_edit(self, request):
        return '<input type="text" name="warpform-%s" value="%s" size="4" />' % (
            self.fieldName(),
            getattr(self.obj, self.col))

    def save(self, val, request):
        try:
            val = int(val)
        except ValueError:
            return u"'%s' is not an integer." % val

        setattr(self.obj, self.col, val)



class DateProxy(BaseProxy):

    jsTemplate = """
<script type="text/javascript">
$(function() { $("#date-field-%s").datepicker(); });
</script>
"""

    dateFormat = "%m/%d/%Y"
    timeFormat = "%H:%M"
    fullFormat = "%s %s" % (dateFormat, timeFormat)


    def render_view(self, request):
        return getattr(self.obj, self.col).strftime(self.fullFormat)


    def render_edit(self, request):
        fieldName = self.fieldName()
        val = getattr(self.obj, self.col)

        dateField = '<input type="text" name="warpform-%s" id="date-field-%s" class="warpform-date" value="%s" size="10" />' % (
            fieldName, fieldName, val.strftime(self.dateFormat))

        timeField = '<input type="text" name="warpform-%s" class="warpform-time" value="%s" size="4" />' % (
            fieldName, val.strftime(self.timeFormat))

        return "%s %s %s" % (dateField, timeField, self.jsTemplate % fieldName)


    def save(self, val, request):
        try:
            # XXX TODO - Timezone according to avatar preferences
            dt = datetime.strptime(val, self.fullFormat).replace(tzinfo=pytz.UTC)
        except ValueError:
            return u"Value '%s' didn't match format '%s'" % (val, self.fullFormat)
        
        setattr(self.obj, self.col, dt)



class ImageProxy(BaseProxy):

    def render_view(self, request):
        return '<img src="%s" />' % url(
            request.node, "image", 
            (self.obj.__class__.__name__, self.obj.id, self.col))


    def render_edit(self, request):
        fieldName = self.fieldName()
        field = '<input type="hidden" name="warpform-%s" class="warpform-upload" />' % fieldName
        iframe = '<iframe name="%s" src="%s" width="300" height="30" id="iframe-%s"></iframe>' % (
            fieldName,
            url(request.node, "uploadframe"),
            fieldName)
        return field + iframe


    def save(self, val, request):
        tf = internal['uploadCache'].get(val)
        if not tf:
            return

        tf.seek(0)
        setattr(self.obj, self.col, tf.read())
        tf.close()
        del internal['uploadCache'][val]
        return



class PriceProxy(BaseProxy):

    def render_view(self, request):
        return "$%i.%.2i" % divmod(getattr(self.obj, self.col), 100)

    def render_edit(self, request):
        return '<input type="text" name="warpform-%s" value="%s" size="8" />' % (
            self.fieldName(),
            self.render_view(request))

    def save(self, val, request):
        val = val.lstrip('$')
        
        try:
            if '.' in val:
                dollars, cents = map(int, val.split('.', 1))
                if cents > 100:
                    return u"Cents must be 0 - 99"
                val = (dollars * 100) + cents
            else:
                val = int(val) * 100
        except ValueError:
            return u"'%s' is not a price." % val

        setattr(self.obj, self.col, val)



class ReferenceProxy(BaseProxy):

    def render_view(self, request):
        obj = getattr(self.obj, self.col)
        crud = obj.__warp_crud__(obj)

        module = getNodeByCrudClass(crud)

        return link(crud.name(request),
                    module, "view", [obj.id])


    def render_edit(self, request):
        obj = getattr(self.obj, self.col)

        reference = self.obj.__class__.__dict__[self.col]

        idCol = reference._local_key[0].name
        noEdit = getattr(self.obj, 'noEdit', [])

        refClass = reference._relation.remote_cls
        crudClass = refClass.__warp_crud__

        if self.col in noEdit or idCol in noEdit:
            return '<input type="hidden" name="warpform-%s" value="%s" />%s' % (
                self.fieldName(), obj.id, crudClass(obj).name(request))

        allObjs = [(crudClass(o).name(request), o) for o in store.find(refClass)]
        allObjs.sort()

        if obj is None:
            sel = lambda o: ""
        else:
            sel = lambda o: ' selected="selected"' if o.id == obj.id else ''


        options = ['<option value="%s"%s>%s</option>' % 
                   (o.id, sel(o), name)
                   for (name, o) in allObjs]

        return '<select name="warpform-%s">\n%s\n</select>' % (
            self.fieldName(), "\n".join(options))


    def save(self, val, request):
        try:
            val = int(val)
        except ValueError:
            return u"Invalid value"
            
        refClass = self.obj.__class__.__dict__[self.col]._relation.remote_cls

        obj = store.get(refClass, val)

        if obj is None:
            return u"No such object (id %s)" % val

        setattr(self.obj, self.col, obj)
        


class ReferenceSetProxy(BaseProxy):
    """
    Currently supports only one-to-many
    """

    def render_view(self, request):

        relation = self.obj.__class__.__dict__[self.col]._relation1
        refClass = relation.remote_cls
        remoteColName = relation.remote_key[0].name

        presets = '{"%s": %s}' % (remoteColName, self.obj.id)
        postData = "{'where': '%s', 'exclude': '[\"%s\"]'}" % (presets, remoteColName.rstrip("_id"))

        noEdit = '["%s"]' % remoteColName

        template = templateLookup.get_template("/crud/list.mak")

        return renderTemplateObj(request, 
                                 template, 
                                 model=refClass.__warp_crud__,
                                 presets=presets,
                                 postData=postData,
                                 noEdit=noEdit,
                                 exclude=[remoteColName.rstrip("_id")])


    def render_edit(self, request):
        return None
