from warp import runtime


def allowed(avatar, obj, **kwargs):

    if avatar is None:
        roles = (runtime.config['roles'][x]
                 for x in runtime.config.get('defaultRoles', []))
    else:
        roles = avatar.roles

    for role in roles:
        opinion = role.allows(obj, **kwargs)
        if opinion is not None:
            return opinion

    return False


# ---------------------------


class Role(object):
    def __init__(self, ruleMap, default=[], name=''):
        self.ruleMap = ruleMap
        self.default = default
        self.name = name

    def allows(self, obj, **kwargs):
        if obj in self.ruleMap:
            rules = self.ruleMap[obj]
        else:
            rules = self.default

        for rule in rules:
            opinion = rule.allows(obj, **kwargs)
            if opinion is not None:
                return opinion


# ---------------------------

class Combine(object):
    combiner = None

    def __init__(self, *checkers):
        self.checkers = checkers

    def allows(self, other, **kwargs):
        return self.combiner(c.allows(other, **kwargs) for c in self.checkers)


class All(Combine):
    combiner = all

class Any(Combine):
    combiner = any

# ---------------------------


class Equals(object):

    def __init__(self, key):
        self.key = key

    def allows(self, other, **kwargs):
        return self.key == other


class Callback(object):

    def __init__(self, callback):
        self.callback = callback

    def allows(self, other, **kwargs):
        return self.callback(other)



# ---------------------------


class Allow(object):
    def allows(self, other, **kwargs):
        return True


class Deny(object):
    def allows(self, other, **kwargs):
        return False


class AllowFacets(object):

    def __init__(self, facets):
        self.facets = facets

    def allows(self, other, facetName=None, **kwargs):
        if not facetName:
            # Always give permissions on the node
            return True
        return facetName in self.facets
