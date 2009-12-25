

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
        return '<input type="text" name="warpform-%s" value="%s" />' % (
            self.fieldName(),
            getattr(self.obj, self.col))


class AreaEditor(BaseEditor):
    
    def render(self):
        return '<textarea name="warpform-%s" cols="30" rows="5">%s</textarea>' % (
            self.fieldName(),
            getattr(self.obj, self.col))


class BooleanEditor(BaseEditor):
    def render(self):
        val = getattr(self.obj, self.col)
        if val:
            checkedBit = 'checked="checked" '
        else:
            checkedBit = ''

        return '<input type="checkbox" name="warpform-%s" class="warpform-bool" value="%s" %s/>' % (
            self.fieldName(), val, checkedBit)


class DateEditor(BaseEditor):

    jsTemplate = """
<script type="text/javascript">
$(function() { $("#date-field-%s").datepicker(); });
</script>
"""

    def render(self):
        fieldName = self.fieldName()
        val = getattr(self.obj, self.col)

        dateField = '<input type="text" name="warpform-%s" id="date-field-%s" class="warpform-date" value="%s" size="10" />' % (
            fieldName, fieldName, val.strftime("%m/%d/%Y"))

        timeField = '<input type="text" name="warpform-%s" class="warpform-time" value="%s" size="4" />' % (
            fieldName, val.strftime("%H:%M"))

        return "%s %s %s" % (dateField, timeField, self.jsTemplate % fieldName)
