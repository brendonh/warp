

class BaseEditor(object):

    def __init__(self, obj, col):
        self.obj = obj
        self.col = col

    def fieldName(self):
        return "%s-%s-%s" % (
            self.obj.__class__.__name__,
            self.obj.id, 
            self.col)



class StringEditor(BaseEditor):
    
    def render(self):
        return '<input type="text" name="%s" value="%s" />' % (
            self.fieldName(),
            getattr(self.obj, self.col))


class AreaEditor(BaseEditor):
    
    def render(self):
        return '<textarea name="%s" cols="30" rows="5">%s</textarea>' % (
            self.fieldName(),
            getattr(self.obj, self.col))


class DateEditor(BaseEditor):

    jsTemplate = """
<script type="text/javascript">
$(function() { $("#%s").datepicker(); });
</script>
"""

    def render(self):
        fieldName = self.fieldName()
        dateFieldName = "%s-date" % fieldName
        timeFieldName = "%s-time" % fieldName
        val = getattr(self.obj, self.col)

        dateField = '<input type="text" name="%s" id="%s" value="%s" size="10" />' % (
            dateFieldName, dateFieldName,
            val.strftime("%m/%d/%Y"))

        timeField = '<input type="text" name="%s" id="%s" value="%s" size="4" />' % (
            timeFieldName, timeFieldName,
            val.strftime("%H:%M"))

        return "%s %s %s" % (dateField, timeField, self.jsTemplate % dateFieldName)
