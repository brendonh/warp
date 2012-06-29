from warp.crud import colproxy, columns
from warp import helpers


class BoundField(object):
    def __init__(self, field, data):
        self.field = field        
        self.data = data

    def render_field(self):
        return self.field.render_field(self.data)

    def render_label(self):
        return self.field.render_label()

    def render_inputs(self):
        return self.field.render_inputs(self.data)

    def render_errors(self):
        return self.field.render_errors()

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def validate(self, request):
        return self.field.validate(self.data, request) 
    

class FormModel(object):
        
    def __init__(self, id=1, fields={}):
        self.id = id
        self.field_value = fields

    _fields = {}
    template = None    

    def _build_field(self, name):
        if name in self._fields.keys():
            return self._fields[name]

        unbound_field = getattr(self, name)
        if not isinstance(unbound_field, colproxy.BaseProxy):
            raise TypeError("Invalid type")

        field = unbound_field.__class__(self, name, valid=unbound_field.validators)
        bound_field = BoundField(field, self.field_value[name] if name in self.field_value.keys() else None)
        self._fields[name] = bound_field

        return bound_field

    def render(self, request):
        return helpers.renderLocalTemplate(request, self.template, form=self)

    def errors(self, name):
        return self._build_field(name).render_errors()

    def inputs(self, name):
        return self._build_field(name).render_inputs()

    def label(self, name):
        return self._build_field(name).render_label()

    def widget(self, name):
        return self._build_field(name).render_field()

    def process(self, request):
        for name, field in self._fields.iteritems():
            fieldName = "%s-%s-%s" % (self.__class__.__name__, self.id, name)
            if fieldName in request.args.keys():
                field.data = request.args.get(fieldName)[0]                    

    def validate(self, request):
        self.process(request)
        errors = []
        success = None
        for name, field in self._fields.iteritems():
            (success, error) = field.validate(request)
            if not success:
                errors.append(error)

        if errors:
            return (False, errors)
        return (True, errors)


class FormSet(object):
    subforms = []    
    def __init__(self, id='1', formModel=None, entries=None):
        self.id = id
        if formModel:
            self.template = formModel.template
        self.expose(formModel, entries)

    template = None
    def render(self, request):
        return helpers.renderLocalTemplate(request, self.template, forms=self)

    def expose(self, FormModel, entries):
        self.subforms[:] = []     

        for idx, entry in enumerate(entries):
            _form = FormModel('n'+str(idx))
            for name, field in _form._fields.iteritems():
                setattr(field, "data", getattr(entry, name) if hasattr(entry, name) else "")     
            self.subforms.append(_form)

    def validate(self, request, extra_validators=None):
        success = True
        for form in self.subforms:
            t = form.validate(request, extra_validators)
            success = success and t
        return success
