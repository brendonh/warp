from warp import runtime


def allowed(avatar, obj, **kwargs):

    if avatar is None:
        roles = (runtime.config['roles'][x]
                 for x in runtime.config.get('defaultRoles', []))
    else:
        roles = avatar.roles

    for role in roles:
        opinion = role.allows(obj, avatar=avatar, **kwargs)
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
        elif obj.__class__ in self.ruleMap:
            rules = self.ruleMap[obj.__class__]
        else:
            rules = self.default

        for rule in rules:
            opinion = rule.allows(obj, **kwargs)
            if opinion is not None:
                return opinion


# ---------------------------


class All(object):
    def __init__(self, *checkers):
        self.checkers = checkers

    def allows(self, other, **kwargs):
        for checker in self.checkers:
            if not checker.allows(other, **kwargs):
                return False
        return True


class Any(object):
    def __init__(self, *checkers):
        self.checkers = checkers

    def allows(self, other, **kwargs):
        for checker in self.checkers:
            if checker.allows(other, **kwargs):
                return True
        return False


class Each(object):
    def __init__(self, *checkers):
        self.checkers = checkers

    def allows(self, other, **kwargs):
        for checker in self.checkers:
            opinion = checker.allows(other, **kwargs)
            if opinion is False:
                return False

        return True


class Not(object):
    def __init__(self, checker):
        self.checker = checker

    def allows(self, other, **kwargs):
        return not self.checker.allows(other, **kwargs)


class If(object):
    def __init__(self, conditionChecker, bodyChecker):
        self.conditionChecker = conditionChecker
        self.bodyChecker = bodyChecker

    def allows(self, other, **kwargs):
        if not self.conditionChecker.allows(other, **kwargs):
            return None
        return self.bodyChecker.allows(other, **kwargs)



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
        return self.callback(other, **kwargs)



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


class DenyFacets(object):

    def __init__(self, facets):
        self.facets = facets

    def allows(self, other, facetName=None, **kwargs):
        if not facetName:
            # Always give permissions on the node
            return True
        return facetName not in self.facets
