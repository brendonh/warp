import pytz, operator, re
from datetime import datetime, date

from warp.runtime import internal, store, templateLookup, exposedStormClasses
from warp.helpers import url, link, getNode, renderTemplateObj, getCrudClass, getCrudObj, getCrudNode


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
        return unicode(getattr(self.obj, self.col) or "")
    
    def render_edit(self, request):
        return u'<input type="text" name="warpform-%s" value="%s" />' % (
            self.fieldName(),
            getattr(self.obj, self.col) or "")


    def save(self, val, request):
        try:
            setattr(self.obj, self.col, val)
        except (TypeError, ValueError):
            return u"Invalid value"
            


class StringProxy(BaseProxy):
    pass


class RawStringProxy(BaseProxy):

    def __init__(self, obj, col, encoding="utf8"):
        self.obj = obj
        self.col = col
        self.encoding = encoding

    def render_view(self, request):
        return (getattr(self.obj, self.col) or "").decode(self.encoding)
    
    def render_edit(self, request):
        return u'<input type="text" name="warpform-%s" value="%s" />' % (
            self.fieldName(),
            getattr(self.obj, self.col) or "")

    def save(self, val, request):
        try:
            setattr(self.obj, self.col, val.encode(self.encoding))
        except (TypeError, ValueError):
            return u"Invalid value"



class NonEmptyStringProxy(StringProxy):

    def save(self, val, request):
        if not val:
            return u"Cannot be empty"
        super(NonEmptyStringProxy, self).save(val, request)



class AreaProxy(StringProxy):

    def __init__(self, obj, col, rows=6, cols=80):
        super(AreaProxy, self).__init__(obj, col)
        self.rows = rows
        self.cols = cols

    def render_view(self, request):
        return u'<div style="white-space: pre">%s</div>' % unicode(getattr(self.obj, self.col) or "")
    
    def render_edit(self, request):
        return u'<textarea name="warpform-%s" cols="%s" rows="%s">%s</textarea>' % (
            self.fieldName(), self.cols, self.rows,
            getattr(self.obj, self.col))


class HTMLAreaProxy(StringProxy):
    
    def render_edit(self, request):
        return u'<textarea name="warpform-%s" cols="80" rows="20" class="markItUp">%s</textarea>' % (
            self.fieldName(),
            getattr(self.obj, self.col))



class BooleanProxy(BaseProxy):

    def render_view(self, request):
        return u"True" if getattr(self.obj, self.col) else u"False"

    def render_edit(self, request):
        val = getattr(self.obj, self.col)
        if val:
            checkedBit = 'checked="checked" '
        else:
            checkedBit = ''

        return u'<input type="checkbox" name="warpform-%s" class="warpform-bool" value="%s" %s/>' % (
            self.fieldName(), val, checkedBit)



class IntProxy(BaseProxy):

    def __init__(self, obj, col, allowNone=False):
        self.allowNone = allowNone
        super(IntProxy, self).__init__(obj, col)


    def render_view(self, request):
        val = getattr(self.obj, self.col)
        if val is None: return "[None]"
        return str(val)


    def render_edit(self, request):
        val = getattr(self.obj, self.col)
        if val is None:
            val = ""
        return u'<input type="text" name="warpform-%s" value="%s" size="4" />' % (
            self.fieldName(), val)

    def save(self, val, request):
        val = val.strip()
        if self.allowNone and not val:
            val = None
        else:
            try:
                val = int(val)
            except ValueError:
                return u"'%s' is not an integer." % val

        setattr(self.obj, self.col, val)


class FloatProxy(BaseProxy):

    def render_edit(self, request):
        return u'<input type="text" name="warpform-%s" value="%s" size="4" />' % (
            self.fieldName(),
            getattr(self.obj, self.col))

    def save(self, val, request):
        try:
            val = float(val)
        except ValueError:
            return u"'%s' is not a float." % val

        setattr(self.obj, self.col, val)


class YearDateProxy(BaseProxy):

    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

    defaultDate = date(1970, 1, 1)

    def render_view(self, request):
        val = getattr(self.obj, self.col)
        if val is None:
            return "[None]"
        return u"%s %s %s" % (val.day, self.months[val.month-1], val.year)

    def render_edit(self, request):
        fieldName = self.fieldName()
        val = getattr(self.obj, self.col)

        if val is None:
            val = self.defaultDate

        def _sel(a, b):
            if a == b: return ' selected="selected"'
            else: return ''
                
        dayField = u'<select name="warpform-%s" class="warpform-stringset">%s</select>' % (
            fieldName, "".join('<option value="%s"%s>%s</option>' % (d, _sel(d, val.day), d)
                               for d in range(1, 32)))

        monthField = u'<select name="warpform-%s" class="warpform-stringset">%s</select>' % (
            fieldName, "".join('<option value="%s"%s>%s</option>' % (i, _sel(i, val.month), self.months[i-1])
                               for i in range(1, 13)))

        yearField = u'<select name="warpform-%s" class="warpform-stringset">%s</select>' % (
            fieldName, "".join('<option value="%s"%s>%s</option>' % (y, _sel(y, val.year), y)
                               for y in range(1950, 2020)))

        return "%s %s %s" % (dayField, monthField, yearField)

    def save(self, val, request):

        try:
            d, m, y = map(int, val)
        except Exception:
            return u"Value wasn't a [day, month, year] list"

        try:
            dt = date(y, m, d)
        except ValueError:
            return u"Value '%s-%s-%s' is not a valid date" % (d, m, y)
                
        setattr(self.obj, self.col, dt)


class DateProxy(BaseProxy):

    jsTemplate = """
<script type="text/javascript">
jQuery(document).ready(function($) { $("#date-field-%s").datepicker(); });
</script>
"""

    dateFormat = "%m/%d/%Y"
    timezone = pytz.UTC

    def render_view(self, request):
        val = getattr(self.obj, self.col)
        if val is None: return u"[None]"
        return val.strftime(self.dateFormat)

    def render_edit(self, request):
        fieldName = self.fieldName()
        val = getattr(self.obj, self.col)

        dateField = u'<input type="text" name="warpform-%s" id="date-field-%s" class="warpform-date" value="%s" size="10" />' % (
            fieldName, fieldName, val.strftime("%m/%d/%Y") if val else "")

        return u"%s %s" % (dateField, self.jsTemplate % fieldName)


    def save(self, val, request):

        try:
            [val,_] = val
        except Exception:
            return u"Value wasn't a [date, 0] list"

        if not val.strip():
            setattr(self.obj, self.col, None)
            return

        try:
            date = (datetime.strptime(val, "%m/%d/%Y")
                    # .replace(tzinfo=self.timezone)
                    # .astimezone(pytz.UTC)
                    .date())
        except ValueError:
            return u"Value '%s' didn't match format '%m/%d/%Y'" % (val, self.dateFormat)
                
        setattr(self.obj, self.col, date)


class DateTimeProxy(DateProxy):

    timeFormat = "%H:%M"
    fullFormat = "%s %s" % (DateProxy.dateFormat, timeFormat)


    def render_view(self, request):
        val = getattr(self.obj, self.col)
        if val is None: return u"[None]"
        return val.astimezone(self.timezone).strftime(self.fullFormat)


    def render_edit(self, request):
        fieldName = self.fieldName()
        val = getattr(self.obj, self.col)

        timeField = u'<input type="text" name="warpform-%s" class="warpform-time" value="%s" size="4" />' % (
            fieldName, val.astimezone(self.timezone).strftime(self.timeFormat) if val else "")

        return u"%s %s" % (super(DateTimeProxy, self).render_edit(request), timeField)


    def save(self, val, request):
        if not val.strip():
            setattr(self.obj, self.col, None)
            return

        try:
            dt = (datetime.strptime(val, self.fullFormat)
                  .replace(tzinfo=self.timezone)
                  .astimezone(pytz.UTC))
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
        val = getattr(self.obj, self.col)
        if val is None:
            return "$0"
        return "$%i.%.2i" % divmod(val, 100)

    def render_edit(self, request):
        return u'<input type="text" name="warpform-%s" value="%s" size="8" />' % (
            self.fieldName(),
            self.render_view(request))

    priceExp = re.compile(r'\$?([0-9]*)(?:\.([0-9]{2})|$)$')

    def save(self, val, request):

        m = self.priceExp.match(val)

        if not m:
            return u"'%s' is not a valid price" % val

        dollars, cents = m.groups()

        if not dollars: dollars = 0
        if not cents: cents = 0

        total = (int(dollars) * 100) + int(cents)

        setattr(self.obj, self.col, total)



class ReferenceProxy(BaseProxy):

    def __init__(self, obj, col, allowNone=False, conditions=(), default=None):
        self.obj = obj
        self.col = col
        self.allowNone = allowNone
        self.conditions = conditions
        self.default = default


    def render_view(self, request):
        obj = getattr(self.obj, self.col)

        if obj is None:
            return ""

        crud = getCrudObj(obj)

        node = getCrudNode(crud)

        return link(crud.name(request),
                    node, "view", [obj.id])


    def render_edit(self, request):

        # Make sure it's loaded
        getattr(self.obj, self.col)

        reference = self.obj.__class__.__dict__[self.col]
        idCol = reference._local_key[0].name
        noEdit = getattr(self.obj, 'noEdit', [])

        # We get the _id field here rather than the reference value
        # itself, because the reference works only on objects that
        # have been added to the store, and we want to avoid that
        # when creating things (since they may not satisfy constraints,
        # and will get added when the database gets flushed on e.g. a find())
        objID = getattr(self.obj, idCol)

        refClass = reference._relation.remote_cls
        crudClass = getCrudClass(refClass)

        if self.col in noEdit or idCol in noEdit:
            obj = store.get(refClass, objID)
            return '<input type="hidden" name="warpform-%s" value="%s" />%s' % (
                self.fieldName(), objID, crudClass(obj).name(request))

        allObjs = [(crudClass(o).name(request), o) for o in store.find(refClass, *self.conditions)]
        allObjs.sort()

        if objID is None:
            if self.default is not None:
                sel = lambda o: ' selected="selected"' if o.id == self.default.id else ''
            else:
                sel = lambda o: ""
        else:
            sel = lambda o: ' selected="selected"' if o.id == objID else ''

        options = []

        if self.allowNone:
            options.append('<option value="">[None]</option>')
        
        options.extend('<option value="%s"%s>%s</option>' % 
                       (o.id, sel(o), name)
                       for (name, o) in allObjs)

        return '<select name="warpform-%s">\n%s\n</select>' % (
            self.fieldName(), "\n".join(options))


    def save(self, val, request):

        try:
            if self.allowNone and val == "":
                val = None
            else:
                val = int(val)
        except ValueError:
            return u"Invalid value"
            
        refClass = self.obj.__class__.__dict__[self.col]._relation.remote_cls

        if val is not None:
            obj = store.get(refClass, val)
            if obj is None:
                return u"No such object (id %s)" % val
            val = obj.id

        # As in render_edit, set the _id col rather than the reference
        # itself, since the latter works only if this object is
        # already in the store
        reference = self.obj.__class__.__dict__[self.col]
        idCol = reference._local_key[0].name
        setattr(self.obj, idCol, val)


class ReferenceSetProxy(BaseProxy):
    """
    Currently supports only one-to-many
    """

    allowCreate = True

    def render_view(self, request):

        refset = self.obj.__class__.__dict__[self.col]

        relation = refset._relation1
        refClass = relation.remote_cls
        remoteColName = relation.remote_key[0].name

        presets = '{"%s": %s}' % (remoteColName, self.obj.id)
        postData = "{'where': '%s', 'exclude': '[\"%s\"]'}" % (presets, remoteColName.rstrip("_id"))

        noEdit = '["%s"]' % remoteColName

        template = templateLookup.get_template("/crud/list.mak")

        return renderTemplateObj(request, 
                                 template, 
                                 model=getCrudClass(refClass),
                                 presets=presets,
                                 postData=postData,
                                 noEdit=noEdit,
                                 exclude=[remoteColName.rstrip("_id")],
                                 allowCreate=self.allowCreate)


    def render_edit(self, request):
        return None
        


class EnumProxy(BaseProxy):

    def __init__(self, obj, col, choices, convertIn=int, noneLabel="None"):
        self.obj = obj
        self.col = col
        self.choices = list(choices)
        self.convertIn = convertIn
        self.noneLabel = noneLabel

    def render_view(self, request):
        val = getattr(self.obj, self.col)
        if val is None:
            return self.noneLabel
        for (k, v) in self.choices:
            if k == val:
                return v
        return "Invalid (%s)" % val
    
    def render_edit(self, request):
        val = getattr(self.obj, self.col)
        options = []
        for (k, v) in self.choices:
            if k == val: sel = ' selected="selected"'
            else: sel = ''
            options.append('<option value="%s"%s>%s</option>' % (k, sel, v))

        return '<select name="warpform-%s">%s</select>' % (
            self.fieldName(), "".join(options))

    def save(self, val, request):
        if self.convertIn is not None:
            try:
                val = self.convertIn(val)
            except (TypeError, ValueError):
                return u"Invalid value"

        if val not in (k for (k,v) in self.choices):
            return u"Invalid value"

        try:
            setattr(self.obj, self.col, val)
        except (TypeError, ValueError):
            return u"Invalid value"



class StormEnumProxy(BaseProxy):

    def __init__(self, obj, col, noneLabel="None"):
        try:
            get_map = obj.__class__.__dict__[col]._variable_kwargs['get_map']
        except KeyError:
            raise ValueError("No choices provided for Enum")
                
        choices = sorted(get_map.iteritems())

        self.obj = obj
        self.col = col
        self.choices = choices
        self.noneLabel = noneLabel


    def render_view(self, request):
        val = getattr(self.obj, self.col)
        if val is None:
            return self.noneLabel
        return val

    
    def render_edit(self, request):
        val = getattr(self.obj, self.col)
        options = []
        for (k, v) in self.choices:
            if v == val: sel = ' selected="selected"'
            else: sel = ''
            options.append('<option value="%s"%s>%s</option>' % (v, sel, v))

        return '<select name="warpform-%s">%s</select>' % (
            self.fieldName(), "".join(options))


    def save(self, val, request):
        try:
            setattr(self.obj, self.col, val.encode("utf-8"))
        except (TypeError, ValueError):
            return u"Invalid value (%s)" % repr(val)
