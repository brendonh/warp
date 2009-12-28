from warp.runtime import store, exposedStormClasses

def applyForm(bits, request):

    errors = []
    actions = []

    for (key, val) in bits.iteritems():

        try:
            model, objID, attr = key.split(u'-')
            objID = int(objID)
        except ValueError:
            errors.append((key, u"Invalid key: %s" % key))
            continue

        try:
            model = exposedStormClasses[model]
        except KeyError:
            errors.append((key, u"Unknown model for key '%s'" % key))
            continue

        try:
            model.__warp_crud__
        except AttributeError:
            errors.append((key, u"Model has no crud class for key '%s'" % key))
            continue

        obj = store.get(model, objID)
        if obj is None:
            errors.append((key, u"Invalid ID for key '%s'" % key))
            continue

        try:
            attr = str(attr)
        except UnicodeEncodeError:
            errors.append((key, u"Invalid attribute name for key '%s'" % key))
            continue

        # XXX TODO -- Access check goes here (or, uh, somewhere)
        # ...

        crud = model.__warp_crud__(obj)
        actions.append( (key, crud, attr, val) )


    if errors:
        return errors


    for (key, crud, attr, val) in actions:
        error = crud.save(attr, val, request)
        if error is not None:
            errors.append((key, error))


    if errors:
        return errors


    return []
