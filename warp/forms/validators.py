import re


class Length(object):    
    def __init__(self, min=-1, max=-1, message=None):
        assert min != -1 or max!=-1, 'At least one of `min` or `max` must be specified.'
        assert max == -1 or min <= max, '`min` cannot be more than `max`.'
        self.min = min
        self.max = max
        self.message = message

    def validate(self, val, request):
        l = val and len(val) or 0
        if l < self.min or self.max != -1 and l > self.max:
            if self.message is None:
                if self.max == -1:
                    self.message = u'Field must be at least %(min)d character long.'
                elif self.min == -1:
                    self.message = u'Field cannot be longer than %(max)d character.'
                else:
                    self.message = u'Field must be between %(min)d and %(max)d characters long.'

            return self.message % dict(min=self.min, max=self.max)
        return None



class File(object):
    def __init__(self, extensions=None, size=None, message="Invalid file"):
        self.message = message
        self.extensions = extensions
        self.size = size
    
    def validate(self, type, size, request):
        if not type or type not in self.extensions:
            return self.message
        if not size or size > self.size:
            return self.message
        return None

class Required(object):

    def __init__(self, message=None):
        self.message = message

    def validate(self, val, request):
        if not val or isinstance(val, basestring) and not val.strip():
            if self.message is None:
                self.message = u'This field is required.'

            return self.message
        return None

class Regexp(object):
    
    def __init__(self, regex, flags=0, message=None):
        if isinstance(regex, basestring):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message

    def validate(self, val, request):
        if not self.regex.match(val or u''):
            if self.message is None:
                self.message = u'Invalid input.'

            return self.message
        return None


class Email(Regexp):

    def __init__(self, message=None):
        super(Email, self).__init__(r'^.+@[^.].*\.[a-z]{2,10}$', re.IGNORECASE, message)

    def validate(self, val, request):
        if self.message is None:
            self.message = u'Invalid email address.'

        return super(Email, self).validate(val, request)


class IPAddress(Regexp):
    
    def __init__(self, message=None):
        super(IPAddress, self).__init__(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', message=message)

    def validate(self, val, request):
        if self.message is None:
            self.message = field.gettext(u'Invalid IP address.')

        return super(IPAddress, self).validate(val, request)


class MacAddress(Regexp):
    
    def __init__(self, message=None):
        pattern = r'^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$'
        super(MacAddress, self).__init__(pattern, message=message)

    def validate(self, val, request):
        if self.message is None:
            self.message = field.gettext(u'Invalid Mac address.')

        return super(MacAddress, self).validate(val, request)


class URL(Regexp):
    
    def __init__(self, require_tld=True, message=None):
        tld_part = (require_tld and ur'\.[a-z]{2,10}' or u'')
        regex = ur'^[a-z]+://([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$' % tld_part
        super(URL, self).__init__(regex, re.IGNORECASE, message)

    def validate(self, val, request):
        if self.message is None:
            self.message = field.gettext(u'Invalid URL.')

        return super(URL, self).validate(val, request)


class UUID(Regexp):
    
    def __init__(self, message=None):
        pattern = r'^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$'
        super(UUID, self).__init__(pattern, message=message)

    def validate(self, val, request):
        if self.message is None:
            self.message = field.gettext(u'Invalid UUID.')

        return super(UUID, self).validate(val, request)


