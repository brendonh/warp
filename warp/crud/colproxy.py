import pytz
from datetime import datetime

from warp.runtime import internal
from warp.helpers import url, getNode


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
