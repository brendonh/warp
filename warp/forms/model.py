
from warp.crud import colproxy, columns
from warp import helpers


try:
    import json
except ImportError:
    import simplejson as json

class FormMeta(type):    
    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls._unbound_fields = None

    def __call__(cls, *args, **kwargs):        
        if cls._unbound_fields is None:
            fields = []            
            for name in dir(cls):
                if not name.startswith('_'):                    
                    unbound_field = getattr(cls, name)                    
                    if hasattr(unbound_field, '_formfield'):
                        fields.append((name, unbound_field))                     
            cls._unbound_fields = fields
        return type.__call__(cls, *args, **kwargs)

    def __setattr__(cls, name, value):        
        if not name.startswith('_') and hasattr(value, '_formfield'):
            cls._unbound_fields = None
        type.__setattr__(cls, name, value)

    def __delattr__(cls, name):        
        if not name.startswith('_'):
            cls._unbound_fields = None
        type.__delattr__(cls, name)

class FormModel(object):
    __metaclass__ = FormMeta
    
    def init(self, fields):
        self._fields = {}

        if hasattr(fields, 'items'):
            fields = fields.items()
        
        for name, unbound_field in fields:
            field = unbound_field.__class__(self, name, valid=unbound_field.validators)
            self._fields[name] = field                 
            setattr(field, "data", self.field_value[name] if name in self.field_value.keys() else "")
        
    def __init__(self, id=1, fields={}):
        self.id = id
        self.field_value = fields
        self.init(self._unbound_fields)

    template = None    

    def render(self, request):
        return helpers.renderLocalTemplate(request, self.template, form=self)

    def errors(self, name):
        return self._fields[name].render_errors()

    def inputs(self, name):
        return self._fields[name].render_inputs()

    def label(self, name):
        return self._fields[name].render_label()

    def widget(self, name):
        return self._fields[name].render_field()

    def process(self, request):
        for name, field in self._fields.iteritems():
            fieldName = "%s-%s-%s" % (self.__class__.__name__, self.id, name)
            if fieldName in request.args.keys():
                setattr(field, "data", request.args.get(fieldName)[0])

    def validate(self, request, extra_validators=None):
        self.process(request)
        self._errors = None
        success = True
        for name, field in self._fields.iteritems():
            if extra_validators is not None and name in extra_validators:
                extra = extra_validators[name]
            else:
                extra = tuple()
            if not field.validate(self, extra):
                success = False
        return success

    def populate_obj(self, obj):       
        for name, field in self._fields.iteritems():
            field.populate_obj(obj, name)

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
